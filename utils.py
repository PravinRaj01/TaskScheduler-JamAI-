import streamlit as st


def setup_sidebar():
    """Setup the common sidebar content for all pages."""
    # Add the logo
    st.sidebar.image("assets/AI logo.webp", use_column_width=True)

    # Add the About section
    st.sidebar.title("About")
    st.sidebar.info(
        """
        **TaskScheduler-JamAI** is a productivity management application that helps you 
        schedule tasks, stay motivated, and organize your day efficiently.

        🔗 [GitHub Repository](https://github.com/PravinRaj01/TaskScheduler-JamAI-.git)
        """
    )
