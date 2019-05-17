# Spotify-Recommeder-and-Playlist-Maker
A recommendation application for Spotify.


## Problem Statement
 
Spotify is one of the most popular and versatile music apps around, but when it comes to music, I believe theres always more you can do. Everyone has their own unique preference for how they like to listen. Sometimes it's about capturing a particular mood, or someone just wants to hear songs that bring them back to a specific time. Some people enjoy exploring particular genres or discovering new artists that may not be as popular or are up and coming. Spotify has two features in its arsenal that I would like to expand upon in this project. The first is a recommender system that acts like a radio channel when you search a song and start playing it. The songs that play after are queued from a recommendation engine built into Spotify. The second is the ability to make custom playlists in the app. My goal is to allow the option for users to approach Spotify in the same way using these two features, but with the added ability to not only customize the recommendation engine to specifically fit the user's needs, but also allow you to automatically make playlists with much more ease than before with the same customizability.

---

## Spotipy and the Spotify API

Spotify's API allows access to data on millions of songs, virtually anything you can think of, and also enables you to interact with your local Spotify device. In order to interface with the API, I will be using a Python library called Spotipy. Supported and developed by Spotify, Spotipy provides a great way to efficiently access the data required to form a recommendation system, to create and modify playlists, and play songs in the Spotify app.

---

## Executive Summary

The purpose of my application is to allow a user to search any song or artist and to play back songs that are similar. The songs can either be played one at a time in a channel format, or added to a playlist and saved in your profile. In addition, the user is
given the option to further personalize the recommendations. They can choose whether they would like to play the original reference song first or skip straight to recommendations. They also can elect to force the recommender to only play an artist once in the queue if this is desired. This is a particularly useful feature for those listeners who are interested in discovery, and provides an option not offered by Spotify. Users can also customize their recommendations with this app based on a popularity range. Spotify ranks every song in its bank by popularity from 0 to 100. If a user wanted to, for example, discover songs that they may not have heard before, they could for example, set the range to only play songs with a popularity between 0 and 25. Or if they wanted to hear only the most popular songs, they could control that as well. Another option users have is to set three possible levels of broadness in the results. This means that if you wanted the songs to be as similar to your song choice as possible, you could set the broadness to narrow. Or if you wanted to allow more flexibility and variety in the results, you could set the broadness to wide.

The system in place for this application involves pulling a list of recommendations from Spotify's API, filtering based on custom options, and then using a model to assess cosine similarity based on the audio features, genres, and popularity of the songs. The data builds on itself every time a new song is put into the queue, and this process can be repeated for as long as the user desires. It also has the ability to automatically play the results on Spotify and to make playlists out of these results. For music lovers, this is a very powerful tool which caters to specific listening preferences and makes it easy to create custom playlists in a streamlined fashion.

---

## Conclusion and Recommendations

Based on testing the results in many different areas of music, I found that the app does a very good job at making recommendations in a way that reasonably follows what is to be expected. The biggest limiting factor in this project is the fact that the original recommendations that are running through the model is limited by what Spotify gives you, however they do a very good job already. This just takes it a step further and allows for more personalization. The broadness settings do make a difference in the results, although the effectiveness of this varies depending on the area of music you are in. If I had a way to access Spotify's entire library of music at once, I would be able to take this recommender to the next level, but for now this is a very effective tool as it is, particularly when it comes to making playlists. In the future, I would like to test more possibilities and see where there could be improvement, and also make this into a web application that could be used by others.
