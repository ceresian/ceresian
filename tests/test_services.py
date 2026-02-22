from app.services import cosine_similarity, weighted_critic_score


def test_cosine_similarity_overlap():
    a = {1: 8.0, 2: 9.0}
    b = {1: 8.0, 2: 9.0, 3: 2.0}
    score = cosine_similarity(a, b)
    assert score > 0.9


def test_cosine_similarity_no_overlap():
    assert cosine_similarity({1: 8.0}, {2: 7.0}) == 0.0


def test_weighted_critic_score():
    score = weighted_critic_score([(0.8, 9.0), (0.2, 5.0)])
    assert score == 8.2


def test_weighted_critic_score_empty():
    assert weighted_critic_score([]) is None
