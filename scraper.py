import streamlit as st
import pandas as pd
import facebook_scraper as fs

def extract_comments_from_post(post_id, max_comments):
    gen = fs.get_posts(post_urls=[post_id], options={"comments": max_comments, "progress": False})
    post = next(gen)
    comments = post['comments_full']
    return comments

def flatten_comments(comment, excluded_fields):
    flattened_comment = {key: value for key, value in comment.items() if key not in excluded_fields}
    flattened_comments = [flattened_comment]

    replies = comment.get('replies', [])
    for reply in replies:
        flattened_comments.extend(flatten_comments(reply, excluded_fields))

    return flattened_comments

def create_csv_file(comments):
    df = pd.DataFrame(comments)
    # 
    return df

def convert_df(df):
    return df.to_csv().encode('utf-8')

excluded_fields = ['commenter_url', 'commenter_meta', 'comment_reactors', 'comment_reactions', 'comment_reaction_count']

def main():
    st.title("Facebook Comment Scraper")

    option = st.sidebar.selectbox("Choose an option", ["Extract URL", "Extract CSV"])

    if option == "Extract URL":
        st.subheader("Extract Comments from Facebook Post URL")

        post_id = st.text_input("Enter Post ID:")
        max_comments = st.slider("Number of Comments to Scrap", 1, 1000, 100)

        if st.button("Generate CSV"):
            with st.spinner("Generating CSV..."):
                comments = extract_comments_from_post(post_id, max_comments)
                flattened_comments = []
                for comment in comments:
                    flattened_comments.extend(flatten_comments(comment, excluded_fields))
                df = create_csv_file(flattened_comments)
                
                st.success("CSV file generated successfully!")

            st.subheader("Preview of the DataFrame (Processed Data):")
            ndf = df.drop('replies',  axis=1)
            st.dataframe(ndf)

            csv = convert_df(ndf)

            st.download_button(
                label="download CSV",
                data=csv,
                file_name="comments_data.csv",
                mime='text/csv',
                help="Press to download the CSV file"
            )

    elif option == "Extract CSV":
        st.subheader("Extract Comments from CSV File")

        uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("Preview of the DataFrame (Raw Data - Before Flattening):")

                max_comments = st.slider("Number of Comments to scrap each post", 1, 1000, 100)

                st.dataframe(df)

                if st.button("Run Extraction"):
                    with st.spinner("Generating CSV..."):
                        all_comments = []
                        for index, row in df.iterrows():
                            post_id = row.get("post_id")
                            comments = extract_comments_from_post(post_id, max_comments)
                            for comment in comments:
                                all_comments.extend(flatten_comments(comment, excluded_fields))

                    st.success("Extraction completed successfully!")

                    st.subheader("Combined DataFrame (Processed Data):")
                    combined_df = pd.DataFrame(all_comments)
                    ndcf = combined_df.drop('replies',  axis=1)
                    st.dataframe(ndcf)

                    com_csv = convert_df(ndcf)

                    st.download_button(
                        label="Download CSV",
                        data=com_csv,
                        file_name="combined_comments_data.csv",
                        mime='text/csv',
                        help="Press to download the combined CSV file"
                    )

            except pd.errors.EmptyDataError:
                st.error("Uploaded file is empty or not in the correct format.")

if __name__ == "__main__":
    main()


# pfbid02m99ffRgzAzqjtDoXqYk1NayUz6ncuM3LusNc5SEbEJL5WADjZMSq9aTuk8Yet1gkl
