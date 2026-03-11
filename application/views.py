from datetime import date
from email.charset import add_charset
from lib2to3.fixes.fix_input import context

from django.contrib import messages
from django.contrib.auth.decorators import login_required
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import requests
from .models import User, Wrapped, TopArtist6
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
from django.shortcuts import get_object_or_404



# Landing page view
def landing_page(request):
    """
    Renders the landing page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered landing page.
    """
    return render(request, 'landing.html')

def login_page(request):
    """
    Renders the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered login page.
    """
    return render(request, 'login.html')

# Spotify OAuth and Data Retrieval Views
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1/me"
SCOPE = "user-follow-read user-top-read user-read-recently-played"

# Spotify login view
def spotify_login(request):
    """
    Initiates the Spotify login process by redirecting the user to the Spotify authorization URL.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to Spotify's authorization page.
    """
    if 'spotify_token' in request.session:
        del request.session['spotify_token']  # Clear any old token

    auth_query_parameters = {
        "response_type": "code",
        "client_id": settings.CLIENT_ID,
        "redirect_uri": settings.REDIRECT_URI,
        "scope": SCOPE,
    }
    url_args = "&".join([f"{key}={value}" for key, value in auth_query_parameters.items()])
    auth_url = f"{SPOTIFY_AUTH_URL}/?{url_args}"
    return redirect(auth_url)

# Spotify callback to retrieve token
def spotify_callback(request):
    """
    Handles Spotify's callback to exchange the authorization code for an access token and fetches user profile data.

    Args:
        request (HttpRequest): The HTTP request object containing the authorization code.

    Returns:
        HttpResponseRedirect: Redirects to the logged-in page on success.
        HttpResponse: Renders an error page if the token retrieval or user profile fetch fails.
    """
    code = request.GET.get('code')

    if not code:
        return render(request, 'error.html', {"message": "No authorization code returned from Spotify."})

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.REDIRECT_URI,
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
    }

    response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)

    if response.status_code != 200:
        return render(request, 'error.html', {"message": f"Failed to retrieve token from Spotify: {response.text}"})

    response_data = response.json()

    access_token = response_data.get('access_token')
    if not access_token:
        return render(request, 'error.html', {"message": "Spotify returned an invalid access token."})

    request.session['spotify_token'] = access_token

    # Fetch the user's Spotify profile to get the username
    user_profile_response = requests.get("https://api.spotify.com/v1/me", headers={
        'Authorization': f'Bearer {access_token}'
    })

    if user_profile_response.status_code == 200:
        user_profile = user_profile_response.json()
        spotify_id = user_profile.get('id')
        username = user_profile.get('display_name')
        current_date = date.today()  # today's date


        request.session['spotify_user_id'] = spotify_id

        # Save the user in the database
        User.objects.update_or_create(
            spotify_id=spotify_id,
            defaults={'username': username}
        )
    else:
        return render(request, 'error.html', {
            "message": f"Failed to fetch user profile from Spotify: {user_profile_response.text}"
        })

    return redirect('loggedIn')


# Fetch user data (top tracks, artists, genres, recently played)
from django.shortcuts import render
import requests

def user_data(request):
    """
    Fetches and processes the user's Spotify data, including top tracks, top artists, genres, and recommendations.
    Saves processed data into the database.

    Args:
        request (HttpRequest): The HTTP request object containing the Spotify access token in the session.

    Returns:
        HttpResponse: Renders a page displaying the user's processed Spotify data.
        JsonResponse: Returns an error message if a Spotify API request fails.
    """
    access_token = request.session.get('spotify_token')
    user_spotify_id = request.session.get('spotify_user_id')
    user, created = User.objects.get_or_create(spotify_id=user_spotify_id)
    if not access_token:
        return render(request, 'error.html', {"message": "No access token found in session"})

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Initialize data structures
    top_artists_data = {
        "4_weeks": [],
        "6_months": [],
        "12_months": []
    }
    top_tracks_data = {
        "4_weeks": [],
        "6_months": [],
        "12_months": []
    }
    genres_data = {
        "4_weeks": set(),
        "6_months": set(),
        "12_months": set()
    }

    # Time ranges corresponding to Spotify API options
    time_ranges = {
        "4_weeks": "short_term",
        "6_months": "medium_term",
        "12_months": "long_term"
    }

    # Fetch data for each time range
    for key, time_range in time_ranges.items():
        # Fetch user's top artists
        top_artists_response = requests.get(
            f"https://api.spotify.com/v1/me/top/artists?time_range={time_range}&limit=50", headers=headers)
        if top_artists_response.status_code == 200:
            top_artists_data[key] = top_artists_response.json().get('items', [])
            # Extract genres from artists
            for artist in top_artists_data[key]:
                genres_data[key].update(artist.get('genres', []))
        else:
            print(f"Failed to fetch top artists for {time_range}:", top_artists_response.text)

        # Fetch user's top tracks
        top_tracks_response = requests.get(
            f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit=50", headers=headers)
        if top_tracks_response.status_code == 200:
            top_tracks_data[key] = top_tracks_response.json().get('items', [])
        else:
            print(f"Failed to fetch top tracks for {time_range}:", top_tracks_response.text)

    # Convert genres sets to lists for JSON serialization
    for key in genres_data:
        genres_data[key] = list(genres_data[key])

    for artist in top_artists_data["6_months"][0:]:
        TopArtist6.objects.update_or_create(
            user=user,
            artist_id=artist.get('id'),
            defaults={
                'name': artist.get('name'),
                'genres': ', '.join(artist.get('genres', []))
            }
        )

    # # Debugging: Print fetched data
    # print("Top Artists (6 months):", top_artists_data["6_months"][:5])  # Show first 5 for brevity
    # print("Top Tracks (6 months):", top_tracks_data["6_months"][:5])
    # print("Genres (6 months):", genres_data["6_months"][:5])  # Show first 5 for brevity


    # Creating necessary lists for slides 4-8
    # Most Recent Tracks
    recent_tracks = requests.get('https://api.spotify.com/v1/me/player/recently-played?limit=5',
                                      headers=headers).json().get('items', [])
    # Convert genres sets to lists for JSON serialization
    for key in genres_data:
        genres_data[key] = list(genres_data[key])

    # Most Recent Tracks
    recent_tracks = requests.get('https://api.spotify.com/v1/me/player/recently-played?limit=5',
                                 headers=headers).json().get('items', [])

    # Prepare the list of song IDs the user has already listened to
    listened_song_ids = set(track['id'] for track in top_tracks_data["6_months"])

    # # Fetch recommendations
    # recommended_songs = get_recommendations(access_token, listened_song_ids, top_tracks_data["6_months"],
    #                                         top_artists_data["6_months"])
    # if recommended_songs:
    #     top_5_songs = random.sample(recommended_songs, min(5, len(recommended_songs)))
    # else:
    #     top_5_songs = []
    # print("Randomly Selected Top 5 Songs:")
    # for song in top_5_songs:
    #     print(f"{song['name']} by {', '.join([artist['name'] for artist in song['artists']])}")
    # # Debugging Spotify's raw recommendations
    # print("Spotify Recommendations (Raw):")  # start of new code
    # for song in recommended_songs:
    #     print(f"{song['name']} by {', '.join([artist['name'] for artist in song['artists']])}")  # end of new code


    # # Debugging Gemini's top 5 recommendations
    # if recommended_songs:
    #     recommended_song = recommended_songs[0]  # Take the first recommendation
    #     recommended_song_details = {
    #         "name": recommended_song['name'],
    #         "artist": ", ".join([artist['name'] for artist in recommended_song['artists']]),
    #         "id": recommended_song['id'],
    #         "image_url": recommended_song['album']['images'][0]['url'] if recommended_song['album']['images'] else None
    #     }
    # else:
    #     recommended_song_details = None
    # Rising Artists

    # Step 1: Assign scores for the 6-month list with a base score for unranked artists
    six_month_scores = {artist['id']: 50 - index for index, artist in enumerate(top_artists_data["6_months"])}
    base_score = -5
    # Give a base score to artists not in the 6-month list later in calculations

    # Step 2: Assign scores for the 4-week list, no base score for unranked artists
    four_week_scores = {artist['id']: 50 - index for index, artist in enumerate(top_artists_data["4_weeks"])}

    # Step 3: Calculate rising scores
    rising_scores = {}
    for artist in top_artists_data["4_weeks"]:
        artist_id = artist['id']
        # Get the 4-week score (exists because we're iterating through 4-week list)
        four_week_score = four_week_scores.get(artist_id, 0)
        # Get the 6-month score, or use the base score if the artist isn't in the 6-month list
        six_month_score = six_month_scores.get(artist_id, base_score)
        # Calculate the rising score
        rising_scores[artist_id] = four_week_score - six_month_score

    # Step 4: Sort artists by rising score, descending, and select the top 5
    # We use top_artists_data["4_weeks"] to keep artist details while ranking by scores
    rising_artists = sorted(
        [artist for artist in top_artists_data["4_weeks"] if artist['id'] in rising_scores],
        key=lambda artist: rising_scores[artist['id']],
        reverse=True
    )[:5]

    # Ghosted Artists

    # Step 1: Assign scores for the 6-month list
    six_month_scores = {artist['id']: 50 - index for index, artist in enumerate(top_artists_data["6_months"])}

    # Step 2: Assign scores for the 4-week list
    four_week_scores = {artist['id']: 50 - index for index, artist in enumerate(top_artists_data["4_weeks"])}

    # Step 3: Calculate ghost scores (only for artists in the 6-month list and not in the 4-week list)
    ghost_scores = {}
    for artist in top_artists_data["6_months"]:
        artist_id = artist['id']
        # Get the 6-month score
        six_month_score = six_month_scores.get(artist_id, 0)
        # Get the 4-week score, or 0 if the artist is not in the 4-week list
        four_week_score = four_week_scores.get(artist_id, 0)
        # Calculate the ghost score
        ghost_scores[artist_id] = six_month_score - four_week_score

    # Step 4: Sort artists by ghost score, descending, and select the top 5
    # Use top_artists_data["6_months"] to keep artist details while ranking by scores
    ghosted_artists = sorted(
        [artist for artist in top_artists_data["6_months"] if artist['id'] in ghost_scores],
        key=lambda artist: ghost_scores[artist['id']],
        reverse=True
    )[:5]

    # Top Artists No Follow
    artist_ids = [artist['id'] for artist in top_artists_data["6_months"]]

    # Convert all IDs to strings and join them with commas
    artist_ids_csl = ",".join(artist_ids)  # No need to map to str, as IDs should already be strings

    params = {
        "type": "artist",
        "ids": artist_ids_csl
    }

    # Spotify API URL for checking follow status
    response = requests.get("https://api.spotify.com/v1/me/following/contains", params=params, headers=headers)

    if response.status_code != 200:
        print("Error:", response.text)
        return JsonResponse({"error": "Failed to fetch data from Spotify"}, status=500)


    # Parse the follow status (list of booleans)
    follow_status = response.json()

    # Ensure follow_status corresponds to the same order as artist_ids
    unfollowed_artists = [
                             artist for artist, is_followed in zip(top_artists_data["6_months"], follow_status) if
                             not is_followed
                         ][:5]  # Take the first 5 unfollowed artists

    # Render only the 6-month data in the template
    if not user_spotify_id:
        return render(request, 'error.html', {"message": "User ID not found in session."})

    user, created = User.objects.get_or_create(spotify_id=user_spotify_id)


    request.session['top_artists_data'] = top_artists_data
    request.session['top_tracks_data'] = top_tracks_data
    request.session['genres_data'] = genres_data
    request.session['recent_tracks'] = recent_tracks
    request.session['rising_artists'] = rising_artists
    request.session['ghosted_artists'] = ghosted_artists
    request.session['top_unfollowed_artists'] = unfollowed_artists

    ## ANIMATION DELAYS ##
    animation_delays = [i * 0.2 for i in range(6)]
    # Render the data in a template
    return render(request, 'user_data.html', {
        "top_artists": top_artists_data["6_months"],
        "top_tracks": top_tracks_data["6_months"],
        "genres": genres_data["6_months"],
        "recent_tracks": recent_tracks,
        # "recommended_songs": recommended_songs,
        "rising_artists": rising_artists,
        "ghosted_artists": ghosted_artists,
        "top_unfollowed_artists": unfollowed_artists,
        # Pass all data for potential access by other parts of the app
        "all_time_data": {
            "top_artists": top_artists_data,
            "top_tracks": top_tracks_data,
            "genres": genres_data
        }
    })

def loggedIn(request):
    """
    Renders the 'loggedIn' page if a Spotify access token is present in the session.
    If no token is found, redirects the user to the Spotify login page.

    Args:
        request: The HTTP request object.

    Returns:
        A redirect to the Spotify login page or renders the 'loggedIn.html' page.
    """
    access_token = request.session.get('spotify_token')
    if not access_token:
        # No token, so redirect to Spotify login
        return redirect('spotify_login')

    # If token exists, render the logged in page
    return render(request, 'loggedIn.html')


def store_past_data(request):
    """
    Stores the user's top songs, artists, and genres into the Wrapped model based on the user's session data.

    This function is triggered by a POST request and retrieves data from the user's session.

    Args:
        request: The HTTP request object.

    Returns:
        Redirects to the 'user_data' page or renders an error page.
    """
    if request.method == "POST":
        # Retrieve Spotify user ID from session
        user_spotify_id = request.session.get('spotify_user_id')
        if not user_spotify_id:
            return render(request, 'error.html', {"message": "User ID not found in session."})

        # Get the user object
        user, created = User.objects.get_or_create(spotify_id=user_spotify_id)

        # Retrieve data from session that was set in user_data view
        top_artists_data = request.session.get('top_artists_data', {})
        top_tracks_data = request.session.get('top_tracks_data', {})
        genres_data = request.session.get('genres_data', {})
        recent_tracks = request.session.get('recent_tracks', [])
        rising_artists = request.session.get('rising_artists', [])
        ghosted_artists = request.session.get('ghosted_artists', [])
        unfollowed_artists = request.session.get('top_unfollowed_artists', [])

        # Save the wrapped data to the database
        wrapped = Wrapped.objects.create(
            user=user,
            top_artists_6_months=top_artists_data.get("6_months", []),
            top_tracks_6_months=top_tracks_data.get("6_months", []),
            genres_6_months=genres_data.get("6_months", []),
            recent_tracks=recent_tracks,
            rising_artists=rising_artists,
            ghosted_artists=ghosted_artists,
            top_unfollowed_artists=unfollowed_artists,
            all_time_top_artists=top_artists_data.get("12_months", []),
            all_time_top_tracks=top_tracks_data.get("12_months", []),
            all_time_genres=genres_data.get("12_months", []),
        )

        return redirect('user_data')
    else:
        return redirect('user_data')




# @login_required
def saved_wrappeds(request):
    """
    Renders a page displaying all saved 'Wrapped' data for the logged-in user.

    Retrieves the user's Spotify ID from the session and fetches the corresponding user object.
    The wrapped data is ordered by creation date in descending order, and the 'saved_wrappeds.html' page is rendered.

    Args:
        request: The HTTP request object.

    Returns:
        Renders the 'saved_wrappeds.html' template with the wrapped data for the user.
    """
    user_spotify_id = request.session.get('spotify_user_id')
    if not user_spotify_id:
        return render(request, 'error.html', {"message": "User ID not found in session."})

    # Get all Wrapped entries for the user, ordered by timestamp
    wrapped_list = Wrapped.objects.filter(user__spotify_id=user_spotify_id).order_by('-timestamp')
    print(f"Wrapped list for user {user_spotify_id}: {wrapped_list}")
    print(wrapped_list.exists())
    # Check if wrapped_list is empty
    if not wrapped_list.exists():  # Use .exists() for efficiency
        return render(request, 'error.html', {"message": "No saved Wrapped data found."})

    # Pass the list of Wrapped entries to the template
    return render(request, 'saved_wrappeds.html', {
        'wrapped_list': wrapped_list
    })



def view_saved_wrapped(request, wrapped_id):
    """
    Displays a detailed view of a specific 'Wrapped' instance based on its ID.

    Retrieves the 'Wrapped' instance by its ID, ensuring the user session is valid, and renders
    the 'saved_data.html' page with the wrapped data for the user.

    Args:
        request: The HTTP request object.
        wrapped_id: The ID of the Wrapped instance to be viewed.

    Returns:
        Renders the 'saved_data.html' template with the selected Wrapped data.
    """
    user_spotify_id = request.session.get('spotify_user_id')
    wrapped = get_object_or_404(Wrapped, id=wrapped_id)

    context = {
        'wrapped': wrapped,
    }

    return render(request, 'saved_data.html', context)

@csrf_exempt
def get_ai_response(request):
    """
    Fetches a response from the Gemini API using a prompt based on the user's top 5 artists.

    This function constructs a prompt using the user's top 5 artists and sends it to the Gemini API for processing.
    The response from the API is returned as a JSON response with a humorous Spotify Wrapped-style blurb.

    Args:
        request: The HTTP request object.

    Returns:
        A JSON response containing the AI-generated text or an error message.
    """
    try:
        gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        headers = {"Content-Type": "application/json"}
        api_key = settings.GOOGLE_GEMINI_KEY

        if not api_key:
            return JsonResponse({"error": "API key is not set"}, status=500)

        # Retrieve the user's Spotify ID from the session
        user_spotify_id = request.session.get('spotify_user_id')
        if not user_spotify_id:
            return JsonResponse({"error": "User ID not found in session."}, status=400)

        # Get the user object
        user = get_object_or_404(User, spotify_id=user_spotify_id)

        # Fetch the top 5 artists for this user from the TopArtist6 model
        top_artists = TopArtist6.objects.filter(user=user)[:5]
        top_artists_string = ", ".join([artist.name for artist in top_artists])

        # Define prompt templates with the dynamically formatted top artists string
        prompts = [
            f"Respond to this in a funny and insightful short blurb for a Spotify Wrapped summary. Keep it under 20 words. Top artists: {top_artists_string}. Describe how a listener of this music would act, think, or dress.",
            f"Summarize in a witty 20-word Spotify Wrapped blurb about a person listening to {top_artists_string}. Describe their personality, clothing style, or habits humorously.",
            f"Create a humorous and unique description (20 words max) for someone whose Spotify Wrapped includes {top_artists_string}. Focus on behaviors and style.",
            f"Write a playful, 20-word blurb summarizing how someone who listens to {top_artists_string} acts, thinks, and dresses."
        ]

        # Randomly select a prompt
        selected_prompt = random.choice(prompts)

        # Define the request body for the AI API
        request_body = {
            "contents": [
                {
                    "parts": [
                        {"text": selected_prompt}
                    ]
                }
            ]
        }

        # Send the request to the Gemini API
        response = requests.post(f"{gemini_url}?key={api_key}", headers=headers, json=request_body)
        response_data = response.json()

        # Extract AI response or handle missing response data
        ai_response = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No content found")

        return JsonResponse({"response": ai_response})

    except Exception as e:
        logging.exception("Error occurred while processing the request")
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)



def get_recommendations(access_token, listened_song_ids, top_tracks, top_artists):
    """
    Fetches music recommendations from the Spotify API based on the user's top tracks and artists.

    This function generates seed artists and tracks, constructs a request to Spotify's recommendations API,
    and filters out tracks already listened to by the user. The function returns new recommendations.

    Args:
        access_token: The Spotify API access token.
        listened_song_ids: List of song IDs the user has already listened to.
        top_tracks: A list of the user's top tracks.
        top_artists: A list of the user's top artists.

    Returns:
        A list of new music recommendations not previously listened to by the user.
    """
    # Generate seed artists and seed tracks
    seed_artists = ",".join([artist['id'] for artist in top_artists[:3]]) if top_artists else ""
    seed_tracks = ",".join([track['id'] for track in top_tracks[:2]]) if top_tracks else ""

    # Ensure at least one seed is provided (fallback seed for testing purposes)
    if not seed_artists and not seed_tracks:
        seed_artists = "4NHQUGzhtTLFvgF5SZesLK"  # Valid fallback artist ID

    # Build the recommendations API URL
    url = f"https://api.spotify.com/v1/recommendations?limit=20"
    if seed_artists:
        url += f"&seed_artists={seed_artists}"
    if seed_tracks:
        url += f"&seed_tracks={seed_tracks}"

    print(f"Generated Spotify Recommendations API URL: {url}")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Make the request to Spotify
    response = requests.get(url, headers=headers)

    # Debugging the response
    if response.status_code == 200:
        recommendations = response.json().get('tracks', [])
        print(f"Fetched Recommendations: {len(recommendations)} tracks found")
        # Filter out tracks already listened to
        new_recommendations = [track for track in recommendations if track['id'] not in listened_song_ids]
        print(f"New Recommendations (not in listened list): {len(new_recommendations)} tracks")
        return new_recommendations
    else:
        # Log detailed error info from Spotify
        print(f"Failed to fetch recommendations. Status Code: {response.status_code}")
        print(f"Response Content: {response.json()}")
        return []

def delete_all_wrappeds(request):
    """
    Deletes all Wrapped entries for the current logged-in user.
    """
    if request.method == "POST":
        user_spotify_id = request.session.get('spotify_user_id')
        if not user_spotify_id:
            messages.error(request, "Error: User not found.")
            return redirect('landing')

        # Delete all Wrapped entries for the user
        Wrapped.objects.filter(user__spotify_id=user_spotify_id).delete()
        messages.success(request, "All Wrapped entries have been successfully deleted.")
        return redirect('landing')

    messages.error(request, "Invalid request method.")
    return redirect('loggedIn')

