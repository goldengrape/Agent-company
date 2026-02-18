from pathlib import Path
import os
import sys

sys.path.insert(0, os.getcwd())

from nanobot.company.loader import CompanyConfigLoader

def main():
    root = Path(os.getcwd())
    print(f"Loading config from {root}")
    loader = CompanyConfigLoader(root)
    loader.load_all()
    
    post_id = "Post_Weather_Analyst"
    if post_id in loader.posts:
        post = loader.posts[post_id]
        print(f"Found Post: {post.title}")
        print(f"Tools: {post.tools}")
        # print(f"Description: {post.description[:50]}...")
    else:
        print(f"Post {post_id} NOT found!")
        print(f"Available posts: {list(loader.posts.keys())}")

if __name__ == "__main__":
    main()
