def jaccard_similarity(text1, text2):
    """returns the jaccard similarity between two lists"""
    intersection_cardinality = len(set.intersection(*[set(text1), set(text2)]))
    union_cardinality = len(set.union(*[set(text1), set(text2)]))
    return intersection_cardinality / float(union_cardinality)


if __name__ == "__main__":
    # 1
    # link: https://www.newscatcherapi.com/blog/ultimate-guide-to-text-similarity-with-python
    # Jaccard Index
    sentences = ["The bottle is nothing empty", "There is nothing in the bottle"]
    sentences = [sent.lower().split(" ") for sent in sentences]
    print(jaccard_similarity(sentences[0], sentences[1]))
