# Imports
import time
import os
import sys
import json
import spotipy
import spotipy.util as util
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.preprocessing import MinMaxScaler

import warnings
warnings.simplefilter(action='ignore')


# Get the username from terminal
username = sys.argv[1]

# Define the scope for the Spotify Client
scope = 'user-read-private user-read-playback-state user-modify-playback-state playlist-modify-public playlist-modify-private'

# Erase cache and prompt for user permission
try:
    token = util.prompt_for_user_token(username, scope)
except:
    os.remove(f'.cache-{username, scope}')
    token = util.prompt_for_user_token(username, scope)

# create our Spotify object with permissions
spotifyObject = spotipy.Spotify(auth=token)

# User information
user = spotifyObject.current_user()
display_name = user['display_name']
userID = user['id']

# Begin user interface
while True:

    # Welcome prompt
    print()
    print()
    print('Welcome to Spotify Recommender ' + display_name + '!')
    print()
    print('0 - Make a playlist')
    print('1 - Make a radio station')
    print('2 - Exit')
    print()
    choice = input('Your choice: ')
    print()

    # For playlist or radio station
    if choice == '0' or choice == '1':

        while True:
            # Get current device
            devices = spotifyObject.devices()
            try:
                deviceID = devices['devices'][0]['id']
                break
            # Ensure that Spotify is open
            except IndexError:
                print()
                print('Please open Spotify on your device to begin.')
                print()
                input('Press enter when ready: ')

        # Select a song or artist
        while True:
            print()
            query = input('Enter a song or artist: ')
            print()

            # Search Spotify for results from the query
            tracks = spotifyObject.search(query, limit=20)
            # A list of track results
            track_list = tracks['tracks']['items']

            # Check if any search results came up
            if len(track_list) == 0:
                print()
                print('No results for that search!')
                continue

            # A dictionary to store the URI for each track in the results
            track_lookup = {}
            # A list to store every artist played
            artists_played_list = []
            # A list to store every song played
            songs_played_list = []

            # Display a menu of song results
            for i in range(len(track_list)):
                print(str(i + 1) + ':', track_list[i]['artists'][0]['name'], '-', track_list[i]['name'])
                # populating the list of arists played to make sure duplicates are not recommended
                artists_played_list.append(track_list[i]['artists'][0]['name'])
                # populating the lookup dictionary
                track_lookup[str(i + 1)] = track_list[i]['uri']
                # populating the list of songs played to make sure duplicates are not recommended
                songs_played_list.append(track_list[i]['uri'])

            while True:
                # Prompt the user to pick from the menu
                print()
                query = input('Enter the number for the correct track, or enter 0 to search again: ')
                print()

                # Account for invalid entries
                try:
                    if int(query) not in range(21):
                        print('Please enter an integer between 0 and 20')
                        continue
                except ValueError:
                    print('Please enter an integer between 0 and 20')
                    continue

                # Option to search again
                if query == '0':
                    break

                break

            # Store the attributes for the song selection
            if query != '0':
                # Store the URI for the song chosen
                first_song_URI = track_lookup[query]
                # Get the track info
                first_song = spotifyObject.track(first_song_URI)
                # Store the song title
                first_song_title = first_song['name']
                # Store the artist
                first_song_artist = first_song['artists'][0]['name']
                # Store the artist's URI
                first_song_artist_URI = first_song['artists'][0]['uri']
                # Store the audio features of the song in a dictionary
                first_song_dict = spotifyObject.audio_features(first_song_URI)[0]
                # Add the name to the dictionary
                first_song_dict['name'] = first_song_title
                # Add the title to the dictionary
                first_song_dict['artist'] = first_song_artist
                # Add the popularity rating to the dictionary
                first_song_dict['popularity'] = first_song['popularity']
                # Getting the genres of the song from the artist info
                genres = spotifyObject.artist(first_song_artist_URI)['genres']
                # Adding the number of genres listed for the song as an entry to the dictionary
                first_song_dict['n_genres'] = len(genres)

                # Loop through genres and add them as entries to the dictionary
                for genre in genres:
                    first_song_dict[f"genre_{genres.index(genre) + 1}"] = genre

                # A list to store the above dicionary and dictionaries for future songs
                full_track_features_list = [first_song_dict]
                break

        # Set up the playlist if playlist option chosen
        if choice == '0':

            # Option for public or private playlist
            while True:
                public = input('Would you like to make this playlist public? (y/n): ')
                print()

                # Account for invalid entries
                if public != 'y' and public != 'n':
                    print('Please select y for yes or n for no.')
                    print()
                else:
                    break

            # Set the playlist privacy option
            if public == 'y':
                public = True
            else:
                public = False

            # Create an empty playlist
            playlist = spotifyObject.user_playlist_create(userID, f'{first_song_artist} - {first_song_title} Playlist', public=public)
            # Get playlist ID and URI
            playlistID = playlist['id']
            playlistURI = playlist['uri']

            # Set the length of the playlist
            while True:
                try:
                    playlist_length = int(input('Playlist length: '))
                # Account for invalid entries
                except ValueError:
                    print()
                    print('Please enter a number.')
                    print()
                    continue
                print()

                # Account for invalid entries
                if playlist_length < 1 or playlist_length > 10_000:
                    print('Please enter a number between 1 and 10,000.')
                    print()
                    continue

                break

        # Set the defaults for customization options
        play_selection = 'y'
        avoid_artist_repeat = 'n'
        pop_min = 0
        pop_max = 100
        broadness = 2

        # User has the option to customize or to go with the default choices
        while True:
            customize = input('Would you like to customize your recommendations? (y/n): ').lower()
            print()

            # With custom options
            if customize == 'y':
                # User has the option to play the selcted song or not
                while True:
                    play_selection = input(f'Would you like to play {first_song_title} first? (y/n): ').lower()
                    print()

                    # Acount for invalid entries
                    if play_selection != 'y' and play_selection != 'n':
                        print('Please select y for yes or n for no.')
                        print()
                    else:
                        break

                # User has the option to avoid playing an artist more than once
                while True:
                    avoid_artist_repeat = input('Do you want to avoid repeating artists? (y/n): ').lower()
                    print()

                    # Account for invalid entries
                    if avoid_artist_repeat != 'y' and avoid_artist_repeat != 'n':
                        print('Please select y for yes or n for no.')
                        print()
                    else:
                        break

                # User has the option to only play songs within a specific popularity range
                while True:
                    pop_range = input('Would you like to set a popularity range to pull from? (y/n): ').lower()
                    print()

                    # Account for invalid entries
                    if pop_range != 'y' and pop_range != 'n':
                        print('Please select y for yes or n for no.')
                        print()
                    else:
                        break

                # Set the popularity range if the user wants to do so
                while True:
                    if pop_range == 'y':
                        # Set the minimum for the popularity range
                        while True:
                            try:
                                pop_min = int(input('Enter a minimum popularity (0 - 100): '))
                                print()
                            # Account for invalid entries
                            except ValueError:
                                print()
                                print('Please enter a number between 0 and 100.')
                                print()
                                continue
                            if pop_min < 0 or pop_min > 90:
                                print('Please enter a number between 0 and 100.')
                                print()
                            else:
                                break

                        # Set the maximum for the popularity range
                        while True:
                            try:
                                pop_max = int(input('Enter a maximum popularity (0 - 100): '))
                                print()
                            # Account for invalid entries
                            except ValueError:
                                print()
                                print('Please enter a number between 0 and 100.')
                                print()
                                continue
                            if pop_max < 10 or pop_max > 100:
                                print('Please enter a number between 0 and 100.')
                                print()
                            else:
                                break

                        # Ensure that the range is set appropriately
                        if pop_max - pop_min < 10:
                            print("The popularity range is too small or your minimum is higher than your maximum.")
                            print("Please make sure your maximum is at least 10 points higher than your minimum.")
                            print()

                        # If no popularity range set
                        else:
                            break

                    # If user chose not to set a range the default is locked in
                    else:
                        break

                # User has the option to set the broadness to narrow, medium or wide
                while True:
                    # Prompt the user to choose broadness level
                    broadness = input('Choose a broadness level (narrow/medium/wide): ').lower()
                    print()

                    # Storing the broadness as an integer
                    if broadness == 'narrow':
                        broadness = 1
                        break
                    elif broadness == 'medium':
                        broadness = 2
                        break
                    elif broadness == 'wide':
                        broadness = 3
                        break
                    # Accounting for invalid entries
                    else:
                        print('Please choose narrow, medium, or wide.')
                        print()

                # Custom options locked in
                break

            # Without custom options
            elif customize == 'n':
                break

            # If yes or no is not chosen for customization options
            else:
                print('Please select y for yes or n for no.')
                print()

        # Play the selected song if user chose to do so
        if play_selection == 'y':
            # For radio stations
            if choice == '1':
                print()
                # Print the artist and title of the starting song
                print('0: ' + first_song_artist + " - " + first_song_title)
                # Start playback
                spotifyObject.start_playback(deviceID, None, [first_song_URI])
                print()
                # Add this arist and to the list of artists played
                artists_played_list.append(first_song_artist)
                # Add this track's URI to the list of songs played
                songs_played_list.append(first_song_URI)

            # For playlists
            else:
                print()
                # Print the artist and title of the starting song
                print('0: ' + first_song_artist + " - " + first_song_title)
                # Add the song to the playlist
                spotifyObject.user_playlist_add_tracks(userID, playlistID, [first_song_URI])
                print()
                # Add this arist and to the list of artists played
                artists_played_list.append(first_song_artist)
                # Add this track's URI to the list of songs played
                songs_played_list.append(first_song_URI)
                # Count off one song in the playlist
                playlist_length -= 1

        # A variable to store the URI for the currently playing song
        current_song_URI = first_song_URI
        # A variable to store the artist for the currently playing song
        current_song_artist = first_song_artist
        # A variable to store the title for the currently playing song
        current_song_title = first_song_title

        # Set a maximum number of songs to play for radio stations
        if choice == '1':
            playlist_length = 10_000

        # Each iteration is for one song played
        for x in range(playlist_length):

            # Generate 25 recommended tracks from the currently playing song
            if broadness == 1:
                # For narrow broadness, base recommendations off of the first track
                recs = spotifyObject.recommendations(seed_tracks=[first_song_URI], limit=25, min_popularity=pop_min, max_popularity=pop_max)
            else:
                # For medium to wide broadness, base recommendations off of the currently playing track
                recs = spotifyObject.recommendations(seed_tracks=[current_song_URI], limit=25, min_popularity=pop_min, max_popularity=pop_max)
            # A list storing the JSON for each recommendation
            rec_list = recs['tracks']
            # A list storing the track URI for each recommendation
            rec_URIs = []
            # A list storing the artist URI for each recommendation
            rec_artist_URIs = []

            # Populate the lists of URIs
            for i in range(len(rec_list)):
                rec_URIs.append(rec_list[i]['uri'])
                rec_artist_URIs.append(rec_list[i]['artists'][0]['uri'])

            # Generate a list of dictionaries containing the audio features for each recommendation
            track_features_list = spotifyObject.audio_features(rec_URIs)

            # Loop through each dictionary in the list
            for i in range(len(rec_list)):
                # Store the song title in the dicionary
                try:
                    track_features_list[i]['name'] = rec_list[i]['name']
                except:
                    # Exit if no song found
                    print('Sorry, Spotify has run out of recommendations!')
                    print('To get more recommendations, you may need to broaden your search.')
                    break
                # Store the artist in the dicionary
                track_features_list[i]['artist'] = rec_list[i]['artists'][0]['name']
                # Store the popularity rating in the dicionary
                track_features_list[i]['popularity'] = rec_list[i]['popularity']
                # Get the URI for the track artist
                track_artist = spotifyObject.artist(rec_artist_URIs[i])
                # Get the list of genres from the artist
                genres = track_artist['genres']
                # Store the number of genres in the dictionary
                track_features_list[i]['n_genres'] = len(genres)

                # Loop through the list of genres
                for genre in genres:
                    # Create an entry in the dicionary for each genre
                    track_features_list[i][f"genre_{genres.index(genre) + 1}"] = genre

            # Add the above list of dictionaries to the full list
            full_track_features_list.extend(track_features_list)

            # Failsafe if no recommendations are found
            if full_track_features_list[-1] == None:
                print('Sorry, no recommendations were found under this criteria.')
                print('Your popularity range may be too small or the selected song')
                print('may be too obscure to find any results.')
                print()
                print('Please try adjusting your search.')
                break


            # Create a dataframe from the list of dictionaries
            try:
                tracks_df = pd.DataFrame(full_track_features_list)
            except:
                break
            # Drop duplicate songs
            tracks_df.drop_duplicates(subset='name', inplace=True)
            # Make the song names the index
            tracks_df.set_index('name', inplace=True)

            # A list of features to assess similarities between songs
            features_list = ['acousticness',
                     'danceability',
                     'energy',
                     'instrumentalness',
                     'liveness',
                     'loudness',
                     'mode',
                     'popularity',
                     'speechiness',
                     'tempo',
                     'time_signature',
                     'valence']


            # Clean up the genre information

            # This list will become a set of all the genres that exist in the dataframe
            unique_genres = []
            # Loop through each genre column
            for i in range(tracks_df['n_genres'].max()):
                # Add all the genres that exist in the column to the total list of genres
                unique_genres.extend(tracks_df[f'genre_{i + 1}'].unique())
                # Create dummy columns from the original genre column
                tracks_df = pd.get_dummies(tracks_df, columns=[f'genre_{i + 1}'])

            # Convert the total list to a set of unique genres
            unique_genres = set(unique_genres)
            # Remove the null value in this set
            if np.nan in unique_genres:
                unique_genres.remove(np.nan)


            # Consolidate all the genre information into simple genre columns

            # Loop through each unique genre
            for genre in unique_genres:
                # A list to store all column names that belong to a specific genre
                same_genre_cols = []
                # Loop through columns in the dataframe
                for col in tracks_df.columns:
                    # Filter only the genre dummy columns
                    if col[:5] == 'genre':
                        # Filter only the columns which begin with genre_1 through genre_9
                        if col[7] == '_':
                            # Filter only the columns which are part of the unique genre
                            if genre == col[8:]:
                                # Add those column names to same_genre_cols
                                same_genre_cols.append(col)

                        # Filter only the columns which begin with genre_10 or higher
                        else:
                            # Filter only the columns which are part of the unique genre
                            if genre == col[9:]:
                                # Add those column names to same_genre_cols
                                same_genre_cols.append(col)

                # Create a new column of all zeros for the unique genre
                tracks_df[genre] = 0
                # Loop through the columns belonging to that genre
                for col in same_genre_cols:
                    # Add the each column to the final genre column
                    tracks_df[genre] += tracks_df[col]

                # Add the name of the newly compiled genre column to the features list
                features_list.append(genre)

            # A datframe with only the relevent features
            model_data = tracks_df[features_list]
            # Scale the popularity ratings between 0 and 1
            model_data['popularity'] = model_data['popularity'] / 100
            # Scale the time_signature, tempo, and loudness between 0 and 1
            minmax = MinMaxScaler()
            model_data[['time_signature', 'tempo', 'loudness']] = minmax.fit_transform(model_data[['time_signature', 'tempo', 'loudness']])
            # Convert the dataframe to a sparse matrix
            tracks_sparse = sparse.csr_matrix(model_data)
            # Calculate the cosine similarity between each song
            recommender = pairwise_distances(tracks_sparse, metric='cosine')
            # Convert the results to a dataframe
            recommender_df = pd.DataFrame(recommender, columns=model_data.index, index=model_data.index)

            if broadness == 3:
                # For a wide broadness, create a list ordering the songs by how similar they are to the current song
                ranked_choices = recommender_df[current_song_title].sort_values()[1:]
            else:
                # For a narrow to medium broadness, create a list ordering the songs by how similar they are to the original song selection
                ranked_choices = recommender_df[first_song_title].sort_values()[1:]

            # A variable to ensure that there is a song to play next
            no_song_found = True


            # Check through the ranked song list to see which one should be played next
            for title in ranked_choices.index:
                # Store the name of the artist
                track_artist = tracks_df.loc[title]['artist']
                # Store the URI of the song
                track_URI = tracks_df.loc[title]['uri']

                # With repeating artists
                if avoid_artist_repeat == 'n':
                    # Make sure that the song has not been played and that the aritst has not been played for the last 4 songs
                    if track_artist not in artists_played_list[-4:] and track_URI not in songs_played_list:
                        # Reset the current song URI
                        current_song_URI = track_URI
                        # Reset the song title
                        current_song_title = title
                        # Reset the artist
                        current_song_artist = track_artist
                        print()
                        print(str(x + 1) + ': ' + track_artist + " - " + title)
                        print()
                        # Add this arist and to the list of artists played
                        artists_played_list.append(current_song_artist)
                        # Add this track's URI to the list of songs played
                        songs_played_list.append(current_song_URI)
                        # Song found
                        no_song_found = False
                        break

                # Without repeating artists
                else:
                    # Make sure that neither the song nor the artist has been played
                    if track_artist not in artists_played_list and track_URI not in songs_played_list:
                        # Reset the current song URI
                        current_song_URI = track_URI
                        # Reset the song title
                        current_song_title = title
                        # Reset the artist
                        current_song_artist = track_artist
                        print()
                        print(str(x + 1) + ': ' + track_artist + " - " + title)
                        print()
                        # Add this arist and to the list of artists played
                        artists_played_list.append(current_song_artist)
                        # Add this track's URI to the list of songs played
                        songs_played_list.append(current_song_URI)
                        # Song found
                        no_song_found = False
                        break

            # Exit if no song found
            if no_song_found:
                print('Sorry, Spotify has run out of recommendations!')
                print('To get more recommendations, you may need to broaden your search.')
                break



            # Interacting with Spotify

            # Playlist option only
            if choice == '0':
                # Add the song to the playlist
                spotifyObject.user_playlist_add_tracks(userID, playlistID, [current_song_URI])
                # Start playing the playlist in Spotify for the first iteration only
                if x == 0:
                    spotifyObject.start_playback(deviceID, playlistURI)
                continue


            # Radio station option only

            # If user does not want to play the original selction first
            if play_selection == 'n':

                # Play the current track
                spotifyObject.start_playback(deviceID, None, [current_song_URI])

                # Tell Spotify when to go to the next song in the queue
                while True:
                    # Sleep for half a second
                    time.sleep(0.5)
                    # Get currently playing track information
                    track = spotifyObject.current_user_playing_track()

                    try:
                        # Whether or not the track is playing
                        on_off = track['is_playing']
                    # If the user closes Spotify
                    except:
                        break
                    # The current progress of the track in miliseconds
                    progress = track['progress_ms']

                    # Control flow for player

                    # Keep the loop going as long as the track is running
                    if on_off == True and progress != 0:
                        # Song is playing
                        song_paused = False
                        continue

                    # Keep the loop going if the song is paused somewhere in the middle of the track
                    elif on_off == False and progress != 0:
                        # Song is paused
                        song_paused = True
                        continue

                    # Keep the loop going if the user pauses the song and then returns to the beginning of the track
                    elif on_off == False and progress == 0 and song_paused == True:
                        continue

                    # Go to the next song
                    else:
                        break

                # In case the user closes Spotify
                devices = spotifyObject.devices()
                try:
                    deviceID = devices['devices'][0]['id']
                except:
                    break

            else:

                while True:
                    # Sleep 1 second
                    time.sleep(0.5)
                    # Current track information
                    track = spotifyObject.current_user_playing_track()

                    try:
                        # Whether or not the track is playing
                        on_off = track['is_playing']
                    # If the user closes Spotify
                    except:
                        break
                    # The current progress of the track in miliseconds
                    progress = track['progress_ms']

                    # Control flow for player

                    # Keep the loop going as long as the track is running
                    if on_off == True and progress != 0:
                        # Song is playing
                        song_paused = False
                        continue

                    # Keep the loop going if the song is paused somewhere in the middle of the track
                    elif on_off == False and progress != 0:
                        # Song is paused
                        song_paused = True
                        continue

                    # Keep the loop going if the user pauses the song and then returns to the beginning of the track
                    elif on_off == False and progress == 0 and song_paused == True:
                        continue

                    # Go to the next song
                    else:
                        break

                # In case the user closes Spotify
                devices = spotifyObject.devices()
                try:
                    deviceID = devices['devices'][0]['id']
                except:
                    break

                # Play the current track
                spotifyObject.start_playback(deviceID, None, [current_song_URI])

    # End the program
    elif choice == '2':
        os.remove(f'.cache-{username}')
        break

    # Accounting for invalid entries
    else:
        print()
        print()
        print('Please enter 0, 1 or 2.')
