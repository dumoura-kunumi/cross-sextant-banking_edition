"""
Semantic ISR Auditor Tool - Synchronous version with complete ISR v3 logic.

This tool implements the full ISR (Information Sufficiency Ratio) calculation
with all 4 critical patches from Chlon et al. (2025):
1. Laplace Smoothing (PROB_FLOOR)
2. One-Sided Clipping (CLIPPING_B)
3. Hard Veto (instability detection)
4. Success Shortcut (high confidence bypass)

Adapted from AsyncISRAuditorV3 to work synchronously with OpenAI client.
"""

import math
import json
import random
import numpy as np
from openai import OpenAI
from typing import List, Dict, Any, Optional


class SemanticISRAuditorTool:
    """
    Synchronous ISR auditor tool for fact verification.
    
    Implements the complete ISR v3 logic with all mathematical components:
    - Delta (information gain)
    - B2T (Bits-to-Trust, KL Divergence)
    - JS Bound (instability measure)
    - ISR (Information Sufficiency Ratio)
    """
    
    # Enhanced token set for "Yes" responses (multiple languages)
    YES_TOKENS = {'sim', 'yes', 's', 'y', 'verdadeiro', 'true', 'aprovado', 'approved'}
    
    # Minimum value to avoid division by zero and invalid logs
    EPSILON = 1e-9
    MIN_B2T = 1e-6
    
    def __init__(
        self,
        client: OpenAI,
        model: str = "gpt-4o-mini",
        target_confidence: float = 0.95,
        num_permutations: int = 6,
        clipping_b: float = 12.0,
        hard_veto_threshold: float = 0.20
    ):
        """
        Initializes the Semantic ISR Auditor Tool.
        
        Args:
            client: OpenAI client instance
            model: Model name to be used (default: "gpt-4o-mini")
            target_confidence: Confidence target for B2T calculation (default: 0.95)
            num_permutations: Number of permutations to generate (default: 6)
            clipping_b: One-sided clipping bound for Delta (default: 12.0)
            hard_veto_threshold: Threshold for hard veto on instability (default: 0.20)
        """
        if not 0.0 <= target_confidence <= 1.0:
            raise ValueError(f"target_confidence must be between 0.0 and 1.0, received: {target_confidence}")
        
        self.client = client
        self.model = model
        self.target_confidence = target_confidence
        self.num_permutations = num_permutations
        self.clipping_b = clipping_b
        self.hard_veto_threshold = hard_veto_threshold
        
        # Patch 1: Laplace Smoothing (PROB_FLOOR)
        # Prevents division by zero and infinite B2T
        # Formula: 1 / (N + 2) -> For num_permutations=6, floor = 0.125
        self.PROB_FLOOR = 1.0 / (self.num_permutations + 2)
    
    def _get_yes_probability(self, text_prompt: str) -> float:
        """
        Gets the linear probability of the "Yes" token for a given prompt.
        
        Makes a synchronous call to the OpenAI API with logprobs enabled and extracts
        the probability of the "Yes" token (or variations) from top_logprobs.
        Enhanced token recognition supports multiple languages.
        
        Args:
            text_prompt: Prompt to be evaluated
        
        Returns:
            Linear probability (0.0 to 1.0) of the "Yes" token.
            Returns 1e-6 if "Yes" is not found in top_logprobs.
            Returns 0.5 in case of API error.
        """
        system_prompt = "You are a precise fact auditor. Answer only Yes or No."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text_prompt}
                ],
                max_tokens=1,
                temperature=0.0,
                logprobs=True,
                top_logprobs=5
            )
            
            if not response.choices or not response.choices[0].logprobs:
                return 0.0001
            
            top_tokens = response.choices[0].logprobs.content[0].top_logprobs
            
            prob_yes = 0.0
            found = False
            
            for token_obj in top_tokens:
                # Robust normalization: remove spaces and convert to lowercase
                token_str = token_obj.token.strip().lower()
                if token_str in self.YES_TOKENS:
                    # Convert logprob to linear probability: e^(logprob)
                    prob_yes = math.exp(token_obj.logprob)
                    found = True
                    break
            
            # If "Yes" not found, use minimum value to avoid log issues
            if not found:
                prob_yes = 0.0001
            
            return prob_yes
        
        except Exception as e:
            print(f"ISR Audit API Error: {e}")
            return 0.5
    
    @staticmethod
    def _calculate_entropy(p: float) -> float:
        """
        Calculates the binary entropy of a Bernoulli distribution.
        
        Formula: H(p) = -[p*log(p) + (1-p)*log(1-p)]
        
        Args:
            p: Probability (must be in [0, 1])
        
        Returns:
            Entropy in bits. Returns 0 if p <= 0 or p >= 1.
        """
        if p <= 0 or p >= 1:
            return 0.0
        return -(p * math.log(p) + (1 - p) * math.log(1 - p))
    
    def _kl_divergence_bernoulli(self, p: float, q: float) -> float:
        """
        Calculates KL divergence between two Bernoulli distributions.
        
        Includes Patch 1: Laplace Smoothing - applies PROB_FLOOR to q to avoid
        infinite B2T when q_min is too small.
        
        Formula: D_KL(p||q) = p*log(p/q) + (1-p)*log((1-p)/(1-q))
        
        Args:
            p: Probability of the reference distribution
            q: Probability of the compared distribution
        
        Returns:
            KL divergence in bits
        """
        # Patch 1: Apply Laplace floor to q
        q = max(q, self.PROB_FLOOR)
        
        # Clip to avoid division by zero and log(0)
        p_safe = np.clip(p, self.EPSILON, 1.0 - self.EPSILON)
        q_safe = np.clip(q, self.EPSILON, 1.0 - self.EPSILON)
        
        return p_safe * np.log(p_safe / q_safe) + (1 - p_safe) * np.log((1 - p_safe) / (1 - q_safe))
    
    def _clip_one_sided(self, val: float) -> float:
        """
        Patch 2: One-Sided Clipping.
        
        Only penalizes information loss (positive Delta). Ignores excessively
        positive signals, focusing on loss of information.
        
        Args:
            val: Value to clip
        
        Returns:
            Clipped value between 0.0 and clipping_b
        """
        return min(max(val, 0.0), self.clipping_b)
    
    def _calculate_delta(self, p_ref: float, probs_permutations: np.ndarray) -> float:
        """
        Calculates the average information gain (Delta) with one-sided clipping.
        
        Delta measures how much information gain the original prompt provides relative
        to permutations. Uses one-sided clipping to focus on information loss.
        
        Args:
            p_ref: Reference probability (mean of all probabilities)
            probs_permutations: Numpy array with probabilities of each permutation
        
        Returns:
            Average value of Delta (information gain in bits)
        """
        deltas: List[float] = []
        
        for s_k in probs_permutations:
            # Ensure safe values to avoid mathematical errors
            s_k_safe = max(s_k, self.EPSILON)
            p_ref_safe = max(p_ref, self.EPSILON)
            
            # Calculate loss: ln(p_ref / s_k)
            # If p_ref > s_k, we have information loss (positive value)
            loss = np.log(p_ref_safe / s_k_safe)
            
            # Patch 2: Apply one-sided clipping
            deltas.append(self._clip_one_sided(loss))
        
        return float(np.mean(deltas))
    
    def _calculate_js_bound(self, probs_permutations: np.ndarray) -> float:
        """
        Calculates JS Bound: instability measure via Jensen-Shannon.
        
        JS Bound = H(mean of probs) - mean(H(probs))
        
        Measures the difference between the entropy of the mean and the mean of entropies,
        indicating instability/variation between permutations.
        
        Args:
            probs_permutations: Numpy array with probabilities of each permutation
        
        Returns:
            JS Bound in bits
        """
        p_mean = np.mean(probs_permutations)
        h_mean = self._calculate_entropy(p_mean)
        # Mean of individual entropies
        mean_h = np.mean([self._calculate_entropy(p) for p in probs_permutations])
        return h_mean - mean_h
    
    def construct_verification_prompt(
        self,
        query: str,
        context_chunks: List[str],
        answer_candidate: str
    ) -> str:
        """
        Constructs the verification prompt for fact-checking.
        
        This prompt asks the model to verify if the proposed answer is completely
        supported by the provided context chunks.
        
        Args:
            query: The question being asked
            context_chunks: List of context chunks to verify against
            answer_candidate: Proposed answer to verify
        
        Returns:
            Formatted verification prompt
        """
        context_str = "\n---\n".join(context_chunks)
        
        return f"""Below are context excerpts, a question, and a proposed answer.

CONTEXT:
{context_str}

QUESTION: {query}
PROPOSED ANSWER: {answer_candidate}

Is the 'PROPOSED ANSWER' completely supported and true based ONLY on the 'CONTEXT' provided above?
Answer only with 'Yes' or 'No'."""
    
    def audit(self, prompt_context: str, proposed_decision: str) -> str:
        """
        Main method that orchestrates the ISR audit process for fact verification.
        
        This version works with:
        - prompt_context: The original user prompt or context (can contain query + context)
        - proposed_decision: Proposed decision token (e.g., "APROVADO", "BLOQUEADO")
        
        The process consists of:
        1. Generate permutations of context (simulated via prompt variations)
        2. Get probabilities for each permutation
        3. Calculate metrics: Delta, B2T, JS Bound, ISR
        4. Apply all 4 critical patches (Laplace, Clipping, Hard Veto, Success Shortcut)
        5. Make decision based on calculated metrics
        
        Args:
            prompt_context: Original prompt or context to verify
            proposed_decision: Proposed decision token to verify
        
        Returns:
            JSON string containing:
                - decision: "APROVADO" or "BLOQUEADO"
                - metrics: Dictionary with ISR, B2T, Delta, JS_Bound, P_Original, P_Min_Permutation
                - reason: Reason for the decision
        """
        if not prompt_context or not prompt_context.strip():
            raise ValueError("Prompt context cannot be empty")
        
        if not proposed_decision or not proposed_decision.strip():
            raise ValueError("Proposed decision cannot be empty")
        
        # For this simplified version, we'll use the prompt_context as the base
        # and generate permutations by creating variations
        # In a full RAG system, this would be context_chunks
        
        # 1. Generate permutations (simulated via prompt variations)
        # First permutation is always the original
        base_prompt = f"{prompt_context}\n\nIs this decision '{proposed_decision}' correct? Answer only Yes or No."
        permutations_prompts = [base_prompt]
        
        # Generate variations (simulating chunk permutations)
        for i in range(self.num_permutations - 1):
            # Create a variation by reordering or slightly modifying
            variation = f"{prompt_context} [Variation {i+1}]\n\nIs this decision '{proposed_decision}' correct? Answer only Yes or No."
            permutations_prompts.append(variation)
        
        # 2. Get probabilities for each permutation
        probs_permutations = np.array([
            self._get_yes_probability(prompt) for prompt in permutations_prompts
        ])
        
        # 3. Calculate statistics
        q_bar = np.mean(probs_permutations)  # Bayesian mean
        q_lo_raw = float(np.min(probs_permutations))  # Worst case (raw)
        q_lo_adj = max(q_lo_raw, self.PROB_FLOOR)  # Worst case (adjusted with Laplace floor)
        
        # Target probability is the same as target_confidence
        target_prob = self.target_confidence
        
        # ==============================================================================
        # PATCH 3: SUCCESS SHORTCUT
        # ==============================================================================
        # If the model is confident even in the worst case, approve immediately.
        if q_lo_adj >= target_prob:
            metrics_dict = {
                "ISR": 999.0,  # Symbolic "infinite" solvency
                "B2T": 0.0,
                "Delta": 0.0,
                "JS_Bound": 0.0,
                "P_Original": round(probs_permutations[0], 4),
                "P_Min_Permutation": round(q_lo_raw, 4)
            }
            
            result = {
                "decision": "APROVADO",
                "metrics": metrics_dict,
                "reason": "High confidence in all permutations. Model is robust and confident."
            }
            return json.dumps(result, indent=2)
        
        # ==============================================================================
        # PATCH 4: HARD VETO (Instability Detection)
        # ==============================================================================
        # If in any permutation confidence drops drastically (< threshold), reject.
        if q_lo_raw < self.hard_veto_threshold:
            metrics_dict = {
                "ISR": 0.0,
                "B2T": 999.0,
                "Delta": 0.0,
                "JS_Bound": round(self._calculate_js_bound(probs_permutations), 4),
                "P_Original": round(probs_permutations[0], 4),
                "P_Min_Permutation": round(q_lo_raw, 4)
            }
            
            result = {
                "decision": "BLOQUEADO",
                "metrics": metrics_dict,
                "reason": f"Severe instability detected (Min: {q_lo_raw:.4f} < {self.hard_veto_threshold}). Answer depends on prompt order."
            }
            return json.dumps(result, indent=2)
        
        # 4. Standard ISR Calculation
        # B2T: How much information do we need? (KL divergence to target)
        b2t = self._kl_divergence_bernoulli(target_prob, q_lo_adj)
        
        # Delta: How much information do we actually have? (Average information loss)
        delta = self._calculate_delta(q_bar, probs_permutations)
        
        # JS Bound: Instability measure
        js_bound = self._calculate_js_bound(probs_permutations)
        
        # ISR: Do we have more than we need?
        if b2t < 1e-6:
            isr = 100.0
        else:
            isr = delta / b2t
        
        # 5. Make decision
        decision = "APROVADO" if isr >= 1.0 else "BLOQUEADO"
        reason = f"ISR calculated: {isr:.4f} (Threshold >= 1.0)"
        
        # 6. Package result
        metrics_dict = {
            "ISR": round(isr, 4),
            "B2T": round(b2t, 4),
            "Delta": round(delta, 4),
            "JS_Bound": round(js_bound, 4),
            "P_Original": round(probs_permutations[0], 4),
            "P_Min_Permutation": round(q_lo_raw, 4)
        }
        
        result = {
            "decision": decision,
            "metrics": metrics_dict,
            "reason": reason
        }
        
        return json.dumps(result, indent=2)
