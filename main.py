import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State, MATCH
import dash_bootstrap_components as dbc
import pyodbc
import urllib.parse
import bcrypt
import logging
import os
from dotenv import load_dotenv
from dash.dependencies import ALL
# Initialize Dash app
archia_app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
archia_app.title = 'Archia'
# Sample data for stories (in a real app, this would be dynamic)
favicon='/assets/content.ico'
load_dotenv()
server = os.getenv("DB_SERVER")
database=os.getenv("DB_DATABASE")
username=os.getenv("DB_USERNAME")
password=os.getenv("DB_PASSWORD")
driver = '{ODBC Driver 17 for SQL Server}'
conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={
                      database};UID={username};PWD={password}')
cursor = conn.cursor()
cursor.execute("SELECT story_id, title, content, author, category, likes FROM stories")
stories = [
    {"story_id": row[0], "title": row[1], "content": row[2], "author": row[3], "category": row[4], "likes": row[5]}
    for row in cursor.fetchall()
]

# App Layout
archia_app.layout = html.Div([
    # Store to track login state
    dcc.Store(id='login-state', data={'user_logged_in': False}),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Login", href="/Login")),
            dbc.NavItem(dbc.NavLink("Register", href="/register")),
            dbc.NavItem(dbc.NavLink("Write a Story", href="/write",
                        id="write-story-link", disabled=True)),
            dbc.NavItem(dbc.NavLink("Read Stories", href="/read",
                        id="read-stories-link", disabled=True)),
        ],
        brand=[html.Img(src='/assets/logo2.png', height="40px", style={"margin-left": "-100px"}),
               html.Span("Archia", style={"margin-left": "10px", "font-size": "2rem", "font-weight": "bold"})],
        brand_href="/",
        color="dark",
        dark=True,
    ),

    dcc.Location(id='url', refresh=False, pathname='/'),
    html.Div(id='page-content'),



    html.Section(id="content-section", children=[
        html.Div([
            html.H1("I think everyone has a story to tell.",
                    className="text-white display-4"),
        ], style={"text-align": "center", "padding": "100px 20px"}),
    ], style={"background-image": "url('/assets/content.png')", "background-size": "cover", "background-position": "center"}),

    # This section will be conditionally rendered based on the URL
    html.Section(id="features-section", children=[
        html.Div([
            html.H2("What Makes Archia Special?",
                    className="text-center my-5"),
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.H3("Write Your Stories"),
                        html.P("Write in a distraction-free environment."),
                    ], className="feature-box"),
                    width=3
                ),
                dbc.Col(
                    html.Div([
                        html.H3("Categorize Your Stories"),
                        html.P("Keep everything neatly archived. With metadata"),
                    ], className="feature-box"),
                    width=3
                ),
                dbc.Col(
                    html.Div([
                        html.H3("Private & Secure"),
                        html.P("Role-based access"),
                    ], className="feature-box"),
                    width=3
                ),
                dbc.Col(
                    html.Div([
                        html.H3("Explore Other Works"),
                        html.P(
                            "Discover, read, and engage with stories from fellow writers."),
                    ], className="feature-box"),
                    width=3
                ),
            ], className="d-flex justify-content-center"),
        ], className="container"),
        # Initially hidden
    ], style={"background-color": "#f4f6f9", "padding": "50px 0", "display": "none"}),
], style={"background": "linear-gradient(to right, #1e2a47, #4b79a1)", "padding": "10px 0"})


# Page content for Homepage
home_page = html.Div([
    html.H1("Welcome to your daily read!", className="text-white display-4"),
    html.P("Write, archive, and share your stories.",
           className="text-white lead"),
    dbc.Button("Start Reading or Writing", href="/Login",
               color="primary", size="lg", className="mt-4"),
    dbc.Row([
        # dbc.Input(id="login-username", placeholder="username", type="username", style={"margin-bottom": "10px"}),
        # dbc.Input(id="login-password", placeholder="Password", type="password", style={"margin-bottom": "10px"}),
        # dbc.Col(dbc.Button("login",  href="/Login", color="primary"), width=12, md=6),
        # dbc.Col(dbc.Button("Register",  href="/register", color="success"), width=12, md=6),
        html.Div(id="login-message")
    ], className="mt-4", align="center"),

    # New section and div below
])


login_page = html.Div([
    html.H1("Let's get you started", className="text-white display-4"),
    html.P("Enter your registered username & password",
           className="text-white lead"),

    dbc.Row([
        dbc.Input(id="login-username", placeholder="username",
                  type="username", style={"margin-bottom": "10px"}),
        dbc.Input(id="login-password", placeholder="Password",
                  type="password", style={"margin-bottom": "10px"}),
        html.P("Navigation tab will activate once logged in",
               className="text-white lead"),
        dbc.Col(dbc.Button("login", id="login-btn",
                color="primary"), width=12, md=6),
        html.Div(id="login-message", className="text-white display-4")
    ], className="mt-4", align="center"),
])

# Registration Page
reg_page = html.Div([
    html.H1("Let's get you started", className="text-white display-4"),
    html.P("Enter a username & password to register",
           className="text-white lead"),
    dbc.Row([
        dbc.Input(id="register-username", placeholder="username",
                  type="username", style={"margin-bottom": "10px"}),
        dbc.Input(id="register-password", placeholder="Password",
                  type="password", style={"margin-bottom": "10px"}),
        dbc.Col(dbc.Button("Register", id="register-btn",
                color="success"), width=12, md=6),
        html.Div(id="register-message")
    ], className="mt-4", align="center"),
])

# Page content for Story Writing Page
write_page = html.Div([
    html.H2("Write Your Story", className="text-white display-4"),
    dbc.Row([
        dbc.Col(dcc.Textarea(id='story-textarea', style={'width': '100%', 'height': '300px'},
                placeholder='Start writing your folklore story here...'), width=12),
        dbc.Col(dbc.Input(id='story-title', placeholder='Story Title',
                style={'margin-top': '10px'}), width=12),
        dbc.Col(dbc.Input(id='author-name', placeholder='Author',
                style={'margin-top': '10px'}), width=12),
        dbc.Col(dbc.Select(
            id='story-category',
            options=[
                {'label': 'Mystery', 'value': 'Mystery'},
                {'label': 'Legend', 'value': 'Legend'},
                {'label': 'Documentary', 'value': 'Legend'},
            ],
            placeholder="Select Story Category",
            style={'margin-top': '10px'}
        ), width=12),
        dbc.Col(dbc.Button("Save Story", id='save-story-btn',
                color="primary", style={'margin-top': '20px'}), width=12),
    ], className="mt-4"),
    html.Div(id='story-save-status')
])

# Page content for Reading Stories   
read_page = html.Div([
    html.H2("Read Stories", className="text-white display-4"),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4(story['title'], className="card-title"),
                    html.P(story['content'][:150] + '...', className="card-text"),
                    html.P(f"Author: {story['author']} - Category: {story['category']}"),
                    dbc.Button(f"Read More", color="primary", href=f"/story/{story['title']}"),
                    html.P(f"Likes: {story['likes']}", id={'type': 'like-count', 'index': story["story_id"]}, className="card-text"),
                    dbc.Button("Like", id={'type': 'like-btn', 'index': story['story_id']}, color="success", size="sm", className="mt-2"),
                    #html.Span(f"Likes: {story.get('likes', 0)}", id={'type': 'like-count', 'index': story['title']}, className="ml-2"),

                ]),
            ], className="mb-4"),
            width=12, md=4
        ) for story in stories
    ], className="mt-4")
])


# Function to connect to DB
def get_db_connection():
    load_dotenv()
    server = os.getenv("DB_SERVER")
    database=os.getenv("DB_DATABASE")
    username=os.getenv("DB_USERNAME")
    password=os.getenv("DB_PASSWORD")
    driver = '{ODBC Driver 17 for SQL Server}'

    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={
            database};UID={username};PWD={password}'
    )
    return conn

# Function to log in a user


def login_user(username, plain_password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    conn.close()

    if user:
        id, stored_hash = user
        if bcrypt.checkpw(plain_password.encode('utf-8'), stored_hash.encode('utf-8')):
            return {"status": "success", "id": id}
        else:
            return {"status": "error", "message": "Invalid password."}
    else:
        return {"status": "error", "message": "User not found."}

# Function to register a user


def register_user(username, plain_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return "Username already exists. Please choose a different username."
    # Hash the password
    password_hash = bcrypt.hashpw(
        plain_password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash.decode('utf-8'))
        )
        conn.commit()
        return "User registered successfully!"
    except Exception as e:
        return f"Error registering user: {e}"
    finally:
        conn.close()



# Callback for user registration
@archia_app.callback(
    Output("register-message", "children"),
    Input("register-btn", "n_clicks"),
    Input("register-username", "value"),
    Input("register-password", "value")
)
def register_callback(n_clicks, username, password):
    if n_clicks:
        return register_user(username, password)
    return ""

# Callback for user login


@archia_app.callback(
    Output("login-message", "children"),
    Output('login-state', 'data'),  # Update the login state
    Input("login-btn", "n_clicks"),
    Input("login-username", "value"),
    Input("login-password", "value")
)
def login_callback(n_clicks, username, password):
    if n_clicks:
        result = login_user(username, password)
        if result["status"] == "success":
            # Set user_logged_in to True and store the username
            return f"Welcome, {username}", {'user_logged_in': True, 'username': username}
        else:
            return result["message"], {'user_logged_in': False, 'username': ''}
    return "", {'user_logged_in': False, 'username': ''}

# Callback to enable/disable navbar links based on login state


@archia_app.callback(
    [
        Output("write-story-link", "disabled"),
        Output("read-stories-link", "disabled"),
    ],
    [Input('login-state', 'data')]  # Track the login state
)
def update_nav_links(state):
    # If the user is logged in, enable both links, else disable them
    if state['user_logged_in']:
        return False, False  # Enable the links
    else:
        return True, True  # Disable the links

# Callback for page content based on URL


@archia_app.callback(
    Output('page-content', 'children'),
    Output('features-section', 'style'),
    Output('content-section', 'style'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/':
        return home_page, {'background-color': "#f4f6f9", 'padding': '50px 0'}, {"background-image": "url('/assets/content.png')", "background-size": "cover", "background-position": "center"}
    elif pathname == '/Login':
        return login_page, {'display': 'none'}, {'display': 'none'}
    elif pathname == '/write':
        return write_page, {'display': 'none'}, {'display': 'none'}
    elif pathname == '/register':
        return reg_page, {'display': 'none'}, {'display': 'none'}
    elif pathname == '/read':
        return read_page, {'display': 'none'}, {'display': 'none'}
    elif pathname.startswith('/story/'):
        story_title = pathname.split('/story/')[1]
        story_title = urllib.parse.unquote(story_title)

        # Find the corresponding story by title
        story = next(
            (story for story in stories if story['title'] == story_title), None)

        if story:
            return html.Div([
                html.H2(story['title'], className="text-white lead", style={
                    "font-family": "Garamond, serif", "font-size": "2.5rem", "font-weight": "bold", "letter-spacing": "1px"
                }),

                dcc.Markdown(
                    # Replace newlines with Markdown-style line breaks
                    story['content'].replace('\n', '  \n'),
                    className="text-white display-4",
                    style={
                        "font-family": "Merriweather, serif", "font-size": "1.25rem", "line-height": "1.75",
                        "letter-spacing": "0.5px", "color": "#f8f9fa", "text-align": "justify",
                        "margin-top": "35px", "margin-bottom": "35px", "max-width": "900px",
                    },
                    dangerously_allow_html=True),
                html.P(f"Author: {
                       story['author']} - Category: {story['category']}", className="text-white lead"),
            ]), {'display': 'none'}, {'display': 'none'}
        else:
            return html.Div([
                html.H2("Story Not Found"),
                html.P("Sorry, we couldn't find the story you're looking for.")
            ]), {'display': 'none'}, {'display': 'none'}
    else:
        return home_page

# Callback for saving a new story with the username of the person who posted it


@archia_app.callback(
    Output('story-save-status', 'children'),
    Input('save-story-btn', 'n_clicks'),
    [
        Input('story-title', 'value'),
        Input('story-textarea', 'value'),
        Input('author-name', 'value'),
        Input('story-category', 'value'),
        Input('login-state', 'data')  # Get the username from login state
    ]
)
def save_story(n_clicks, title, content, author, category, state):
    if n_clicks is None:
        return ""

    if not title or not content or not category:
        return dbc.Alert("Please fill in all fields.", color="danger")

    if not state['user_logged_in']:
        return dbc.Alert("You must be logged in to post a story.", color="danger")

    username = state['username']  # Get the logged-in user's username

    try:
        cursor.execute(
            "INSERT INTO stories (title, content, author, category, posted_by) VALUES (?, ?, ?, ?, ?)",
            # Include the username who posted the story
            (title, content, author, category, username)
        )
        conn.commit()
        return dbc.Alert("Story saved successfully!", color="success")
    except Exception as e:
        return dbc.Alert(f"Error saving story: {str(e)}", color="danger")
# Callback for like button press
from dash.exceptions import PreventUpdate

@archia_app.callback(
    Output('like-status', 'children'),
    [Input({'type': 'like-btn', 'index': ALL}, 'n_clicks')],
    [State('login-state', 'data')]  # Changed to 'login-state' to match your earlier setup
)
def like_story(n_clicks, login_state):
    if not login_state['user_logged_in']:
        return "You must be logged in to like stories"
    if n_clicks is None:
        return dash.no_update  # No update if no button has been clicked
    
    updated_likes = []    
    
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
        
    
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        story_id = eval(triggered_id)['index']

    for idx, clicks in enumerate(n_clicks):
        if clicks is not None and clicks > 0:
            # Here you should increment the likes count in the database for the specific story
            story_id = idx + 1  # Use actual logic to fetch the correct story ID

        # Log the clicked story_id for debugging purposes
        print(f"Story {story_id} liked by {username}")

        # Connect to SQL Server using pyodbc

        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to get the current like count
        cursor.execute("SELECT likes FROM stories WHERE story_id = ?", (story_id,))
        current_likes = cursor.fetchone()
            
        if current_likes:
            new_like_count = current_likes[0] + 1
            # Update the like count in the database
            cursor.execute("UPDATE stories SET likes = ? WHERE story_id = ?", (updated_likes, story_id))
            conn.commit()

            conn.close()
            updated_likes.append(f"Likes: {clicks + 1}")  # For demonstration, increment like count
            
    return new_like_count


# Running the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))    
    archia_app.run_server(port=port)
