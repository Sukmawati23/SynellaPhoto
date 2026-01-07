def countdown(root, seconds, callback, done):
    if seconds <= 0:
        done()
        return
    callback(seconds)
    root.after(1000, lambda: countdown(root, seconds - 1, callback, done))
