import os
import requests
from github import Github
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

# Ensure you have these packages installed:
# pip install requests PyGithub scikit-learn nltk matplotlib

# Initialize GitHub API (use your own access token)
GITHUB_ACCESS_TOKEN = 'your_github_access_token'
g = Github(GITHUB_ACCESS_TOKEN)

# Function to preprocess text
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    return ' '.join(filtered_tokens)

# Function to fetch repository content
def fetch_repo_content(repo):
    contents = repo.get_contents("")
    repo_text = ""
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            repo_text += requests.get(file_content.download_url).text
    return repo_text

# Function to categorize repositories
def categorize_repos(repos):
    repo_texts = []
    for repo in repos:
        repo_texts.append(preprocess_text(fetch_repo_content(repo)))
    
    # Vectorize the text data
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(repo_texts)
    
    # Cluster the repositories
    num_clusters = 5
    km = KMeans(n_clusters=num_clusters)
    km.fit(X)
    
    # Visualize the clusters
    pca = PCA(n_components=2)
    scatter_plot_points = pca.fit_transform(X.toarray())
    colors = ["r", "b", "c", "y", "m"]
    
    x_axis = [o[0] for o in scatter_plot_points]
    y_axis = [o[1] for o in scatter_plot_points]
    
    fig, ax = plt.subplots(figsize=(20,10))
    
    ax.scatter(x_axis, y_axis, c=[colors[d] for d in km.labels_])
    
    plt.show()
    
    return km.labels_

# Fetch user repositories
def fetch_user_repositories(username):
    user = g.get_user(username)
    return user.get_repos()

# Main function
def main(username):
    repos = fetch_user_repositories(username)
    labels = categorize_repos(repos)
    
    # Tag repositories based on their categories
    categories = ["Category1", "Category2", "Category3", "Category4", "Category5"]
    for repo, label in zip(repos, labels):
        repo.create_label(name=categories[label], color="f29513")
        print(f'Repository {repo.name} categorized as {categories[label]}')

if __name__ == "__main__":
    username = "your_github_username"
    main(username)
