from pytube import YouTube

link = 'https://www.youtube.com/watch?v=nFIfv-jIgbI'
# YouTube(link).streams.first().download()
yt = YouTube('https://www.youtube.com/watch?v=nFIfv-jIgbI')
# yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
stream = yt.streams.get_highest_resolution()
stream.download()