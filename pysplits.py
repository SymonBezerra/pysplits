import time
import threading
from pynput import keyboard

start_time = None
elapsed_time = 0
running = False

hotkeys = {
    's': 'start',
    't': 'stop',
    'r': 'reset',
    'q': 'quit'
}

# ADD YOUR SPLITS HERE!
splits = ['Game 1', '1st Match', '2nd Match', 'Semi-final', 'Final']
splits_time = [0] * len(splits)
current_split = 0

split_event = threading.Event()
exit_flag = threading.Event()

def on_press(key):
    global start_time, elapsed_time, running, current_split, splits_time, exit_flag

    try:
        if key.char in hotkeys:
            action = hotkeys[key.char]
            if action == 'start':
                if not running:
                    start_time = time.time() - elapsed_time
                    running = True
                elif running:
                    split_event.set()
            elif action == 'stop':
                if running:
                    elapsed_time = time.time() - start_time
                    running = False
            elif action == 'reset':
                start_time = None
                elapsed_time = 0
                running = False
                current_split = 0
                splits_time = [0] * len(splits)
            elif action == 'quit':
                exit_flag.set()
                return False 
    except AttributeError:
        pass

def format_time(current_time):
    minutes, seconds = divmod(current_time, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = int((current_time - int(current_time)) * 1000)
    return f'{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{milliseconds:03}'

def display_time():
    global current_split, running, exit_flag
    while not exit_flag.is_set():
        if running:
            current_time = time.time() - start_time
        else:
            current_time = elapsed_time

        print('\033[H\033[J', end='')

        for i in range(len(splits)):
            if i != current_split:
                print(f'{splits[i]}: {format_time(splits_time[i])}')
            else:
                print(f'{splits[i]}: {format_time(current_time)}')

        if split_event.is_set():
            split_event.clear()
            if current_split < len(splits):
                splits_time[current_split] = current_time
                current_split += 1
            else: running = False

        time.sleep(0.01)

if __name__ == "__main__":
    display_thread = threading.Thread(target=display_time)
    display_thread.daemon = True
    display_thread.start()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    exit_flag.set()
    display_thread.join()