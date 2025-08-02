import os
from hn import HN

def main():
    hn = HN()

    # Log in to Hacker News
    hn.login(os.environ.get("HN_USERNAME"), os.environ.get("HN_PASSWORD"))

    # Submit a test post
    submission = hn.submit("Test post for watching_u_watching", url="https://github.com/genaforvena/watching_u_watching", text="This is a test post for the watching_u_watching project.")

    # Get the post ID
    post_id = submission.id

    # Delete the post
    hn.delete_post(post_id)

if __name__ == '__main__':
    main()
