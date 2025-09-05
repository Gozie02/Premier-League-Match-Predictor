from scipy.stats import poisson
import numpy as np
# --------------------------------------------------------
# Probability utilities
# --------------------------------------------------------
def poisson_probs(mu_home, mu_away, max_goals=10):
    """Compute full probability matrix for home vs away goals up to max_goals"""
    home_p = [poisson.pmf(i, mu_home) for i in range(max_goals+1)]
    away_p = [poisson.pmf(i, mu_away) for i in range(max_goals+1)]
    return np.outer(home_p, away_p)

def derive_probabilities(mu_home, mu_away):
    """Derive outcome & over/under probabilities from predicted means"""
    prob_matrix = poisson_probs(mu_home, mu_away)

    # Outcome probabilities
    p_home_win = np.sum(np.tril(prob_matrix, -1))
    p_draw = np.sum(np.diag(prob_matrix))
    p_away_win = np.sum(np.triu(prob_matrix, 1))

    # Over/Under probabilities
    goal_probs = {}
    for line in [1.5, 2.5, 3.5]:
        total_probs = [prob_matrix[i, j] for i in range(prob_matrix.shape[0])
                       for j in range(prob_matrix.shape[1])]
        total_goals = [i+j for i in range(prob_matrix.shape[0])
                       for j in range(prob_matrix.shape[1])]

        under_prob = np.sum([p for g, p in zip(total_goals, total_probs) if g <= line])
        over_prob = 1 - under_prob
        goal_probs[f"under_{line}"] = under_prob
        goal_probs[f"over_{line}"] = over_prob

    return {
        "p_home_win": p_home_win,
        "p_draw": p_draw,
        "p_away_win": p_away_win,
        **goal_probs
    }
