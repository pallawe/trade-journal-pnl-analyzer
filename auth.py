import streamlit as st
from supabase import create_client


@st.cache_resource
def get_supabase_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


def sign_up(email, password):
    supabase = get_supabase_client()
    return supabase.auth.sign_up({
        "email": email,
        "password": password
    })


def sign_in(email, password):
    supabase = get_supabase_client()
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })


def sign_out():
    supabase = get_supabase_client()
    supabase.auth.sign_out()


def show_auth_page():
    st.title("📈 Trade Journal Pro")
    st.caption("Manage your trades. Track your performance.")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Welcome Back")

        email = st.text_input("Email Address", key="login_email")
        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True):
            if not email or not password:
                st.warning("Please enter email and password.")
            else:
                try:
                    response = sign_in(email, password)
                    st.session_state["user"] = response.user
                    st.success("Login successful!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

    with tab2:
        st.subheader("Create Account")

        new_email = st.text_input(
            "Email Address",
            key="signup_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        if st.button("Create Account", use_container_width=True):
            if not new_email or not new_password:
                st.warning("Please enter email and password.")
            elif len(new_password) < 8:
                st.warning("Password must be at least 8 characters.")
            else:
                try:
                    response = sign_up(new_email, new_password)

                    if response.session is None:
                        st.success(
                            "Account created! Please verify your email before logging in."
                        )
                    else:
                        st.success("Account created successfully!")

                except Exception as e:
                    st.error(f"Registration failed: {e}")