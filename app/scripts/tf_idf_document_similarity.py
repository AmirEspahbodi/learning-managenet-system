# link: https://thinkinfi.com/document-similarity-matching-using-tf-idf-python/
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string


def tf_idf_cosine_similarity(target_document, documents, threshold=0.5):
    # Example documents

    # Step 3: Preprocessing the documents
    def preprocess_document(document):
        # Tokenization
        tokens = word_tokenize(document)
        # Lowercase conversion
        tokens = [token.lower() for token in tokens]
        # Punctuation removal
        tokens = [token for token in tokens if token not in string.punctuation]
        # Stop word removal
        stop_words = set(stopwords.words("english"))
        tokens = [token for token in tokens if token not in stop_words]
        # Stemming
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]
        return " ".join(tokens)

    preprocessed_documents = [preprocess_document(document) for document in documents]

    # Step 4: Compute TF-IDF values
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(preprocessed_documents)

    # # Convert TF-IDF document term matrix to DataFrame
    # feature_names = vectorizer.get_feature_names_out()
    # df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)

    # # Print the TF-IDF DataFrame
    # # print("\nTF-IDF DataFrame:")
    # # print(df_tfidf)

    # Step 5: Build TF-IDF vectors

    # Example: Convert a new document into a TF-IDF vector
    new_preprocessed_document = preprocess_document(target_document)
    new_tfidf_vector = vectorizer.transform([new_preprocessed_document])

    # # Convert TF-IDF matrix to DataFrame
    # feature_names = vectorizer.get_feature_names_out()
    # df_tfidf_new = pd.DataFrame(new_tfidf_vector.toarray(), columns=feature_names)

    # Print the TF-IDF DataFrame
    # print("\nTF-IDF DataFrame:")
    # print(df_tfidf_new)

    # Step 6: Measure document similarity

    # Compute cosine similarity between the new document and all other documents
    similarity_scores = cosine_similarity(new_tfidf_vector, tfidf_matrix)
    # print(similarity_scores)

    # Step 7: Rank the document similarity
    similarity_scores = similarity_scores.flatten()  # Convert to 1D array
    document_indices = similarity_scores.argsort()[
        ::-1
    ]  # Sort indices in descending order

    cheetes = []
    for index in document_indices:
        if (
            similarity_scores[index] > threshold
        ):  # Exclude the new document itself (similarity score = 1)
            cheetes.append((index, similarity_scores[index]))
    return cheetes


def find_cheeters(documents):
    cheeters = [[] for _ in range(len(documents))]
    for i in range(len(documents) - 1):
        cheets = tf_idf_cosine_similarity(documents[i], documents[i + 1 :])
        for cheet in cheets:
            cheeters[i].append(int(cheet[0] + i + 1))
            cheeters[i].append(cheet[1])
    return cheeters
