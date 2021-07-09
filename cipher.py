#How should program exit? Sys.exit
#
from curses import wrapper
import curses
from curses.textpad import Textbox, rectangle
from timeit import timeit
from ctypes import *

def cipher(message, key):
    return bytes([message[i] ^ key[i % len(key)] for i in range(0, len(message))])

def load_rust_cipher_lib():
  lib = cdll.LoadLibrary("./lib_rust_xorcipher.so")
  lib.cipher.restype = None
  lib.cipher.argtypes = [c_char_p, c_char_p, c_char_p, c_int, c_int]
  return lib

def load_c_cipher_lib():
  lib = cdll.LoadLibrary("./lib_c_xorcipher.so")
  lib.cipher_pure.restype = None
  lib.cipher_pure.argtypes = [c_char_p, c_char_p, c_char_p, c_int, c_int]
  return lib

def enter_is_terminate(x):
    if x == 10:
        return 7
    return x


class Application:
    def __init__(self, screen):
        self.screen = screen
        self.screen.clear()
        self.window = curses.newwin(24,80,0,0)
        self.window.box()
        self.window.addstr(1,25,"Welcome to the XOR-Cipher App!")
        self.menu = self.create_menu()
        self.value = "This is a haiku; it is not too long I think; but you may disagree".encode('cp437')
        self.key =  "But there's one sound that no one knows... What does the Fox say?".encode('cp437')
        self.status = "Status: Application started successfully."
        self.uiprompt = None
        self.benchmarks = None
        self.display = self.create_display()
        self.uiwin = curses.newwin(6,78,17,1)
        self.textwin = self.uiwin.subwin(3,68,19,6)
        self.textinside = self.textwin.subwin(1,66,20,7)
        self.ctrl_translation = str.maketrans(bytes(range(0,32)).decode("cp437"), "�☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼")
        self.draw()


    def draw(self):
        self.screen.addstr(24,1," " * 72)
        self.screen.addstr(24,1,self.status)
        width = 78
        if self.uiprompt != None:
            self.uiwin.box()
            self.uiwin.addstr(1,round((width - len(self.uiprompt))/2) , self.uiprompt)
            self.textwin.box()
        elif self.benchmarks != None:
            self.uiwin.box()
            if (self.benchmarks == 0):  #  Running
                self.uiwin.addstr(1,round((width - 22)/2) , "Running benchmarks....")
            else:
                self.uiwin.addstr(1,round((width - 23)/2) , "Results from Benchmark")
                r,p,c = self.benchmarks
                c_string = "C Cipher:" + " " * (23-13-len(c)) + c
                self.uiwin.addstr(2,round((width - 23)/2), (c_string))
                r_string = "Rust Cipher:" + " " * (23-13-len(r)) + r
                self.uiwin.addstr(3,round((width - 23)/2), (r_string))
                p_string = "Python Cipher:" + " " * (23-15-len(p)) + p
                self.uiwin.addstr(4,round((width - 23)/2), p_string)
        else:
            self.uiwin.clear()
            self.textwin.clear()
            self.textinside.clear()
        self.refresh()
    
    def refresh(self):
        self.write_display()
        self.screen.refresh()
        self.window.refresh()
        self.menu.refresh()
        self.display.refresh()
        self.uiwin.refresh()
    
    def write_display(self):
        self.display.addstr(1,2," " * 72)
        self.display.addstr(2,2," " * 72)
        self.display.addstr(1,2,"TEXT [" + self.value.decode('cp437').translate(self.ctrl_translation) + "]")
        self.display.addstr(2,2,"KEY  [" + self.key.decode('cp437').translate(self.ctrl_translation) + "]")
        return

    def create_menu(self):
        menu = curses.newwin(10,40,2,20)
        menu.box()
        menu.addstr(1,2,"[F] Read text from a local File")
        menu.addstr(2,2,"[I] Read text from user Input prompt")
        menu.addstr(3,2,"[R] Apply Rust cipher to this text")
        menu.addstr(4,2,"[P] Apply Python cipher to this text")
        menu.addstr(5,2,"[C] Apply C cipher to this text")
        menu.addstr(6,2,"[K] Change Key used for ciphers")
        menu.addstr(7,2,"[B] Run Benchmarks on text (100000x)")
        menu.addstr(8,2,"[Q] Quit the Application")
        return menu

    def create_display(self):
        display = curses.newwin(4,76,12,2)
        display.box()
        return display
    
    def read_file(self):
        width = 78
        self.uiprompt = "Enter file to load below, then press [ENTER]"
        textbox = curses.textpad.Textbox(self.textinside)
        self.draw()
        textbox.edit(enter_is_terminate)
        path = textbox.gather()
        if path == "":
            self.uiprompt = None
            self.status = "Status: File load cancelled."
        else:
            path = validateTextbox(path).encode('cp437')
            self.uiprompt = None
            try:
                with open(path,'r',encoding='cp437') as file:
                    val = file.readline()
                    self.value = val[:65].encode('cp437')
                    self.status = "Status: File contents loaded successfully."
            except Exception as e:
                self.status = "Status: ERROR: COULD NOT LOAD FILE: " + path.decode('cp437').translate(self.ctrl_translation) + "."
        self.draw()
        
    def new_text(self):
        self.uiprompt = "Enter new text below, then press [ENTER]"
        textbox = curses.textpad.Textbox(self.textinside)
        self.draw()
        textbox.edit(enter_is_terminate)
        text = textbox.gather()
        text = validateTextbox(text)
        self.uiprompt = None
        if text == "":
            self.status = "Status: Cancelled user input of text (empty string)."
        else:
            self.value = text.encode('cp437')
            self.status= "Status: New text loaded into memory from user input."
        self.draw()

    def new_key(self):
        self.uiprompt = "Enter new key and then press [ENTER]"
        textbox = curses.textpad.Textbox(self.textinside)
        self.draw()
        textbox.edit(enter_is_terminate)
        text = textbox.gather()
        text = validateTextbox(text)
        self.uiprompt = None
        if text == "":
            self.status = "Status: Cancelled user input of key (empty string)."
        else:
            self.status = "Status: New key loaded into memory from user input."
            self.key = text.encode('cp437')
        self.draw()

    def python_cipher(self, write=True):
        res = cipher(self.value,self.key)
        if write:
            self.value = res
            self.status = "Status: Applied Python cipher."
            self.draw()
        return res
    
    def rust_cipher(self, write=True):
        text = "This is an example message".encode('cp437')
        key = "My sample key".encode('cp437')
        lib = load_rust_cipher_lib()
        buf = create_string_buffer(len(text))
        lib.cipher(text,key,buf,len(text), len(key))
        self.status = "Status: Applied Rust cipher"
        if write:
            self.value = buf[0:len(text)]
            self.status = "Status: Applied Rust cipher."
            self.draw()
        return buf[0:len(text)]
        
    def c_cipher(self, write=True):
        text = self.value
        key = self.key
        lib = load_c_cipher_lib()
        buf = create_string_buffer(len(text))
        lib.cipher_pure(text,key,buf,len(text), len(key))
        self.status = "Status: Applied C cipher"
        if write:
            self.value = buf[0:len(text)]
            self.status = "Status: Applied C cipher."
            self.draw()
        return buf[0:len(text)]

    def run_benchmarks(self):
        self.benchmarks = 0
        self.draw()
        text = self.value
        key = self.key
        rust_lib = load_rust_cipher_lib()
        buf = create_string_buffer(len(text))
        python = timeit(lambda: cipher(text,key), number=100000)
        rust = timeit(lambda: rust_lib.cipher(text,key,buf,len(text), len(key)), number=100000)
        c_lib = load_c_cipher_lib()
        buf = create_string_buffer(len(text))
        python = timeit(lambda: cipher(text,key), number=100000)
        c = timeit(lambda: c_lib.cipher_pure(text,key,buf,len(text), len(key)), number=100000)
        ps = str("%06.3f" % python)
        rs = str("%06.3f" % rust)
        cs = str("%06.3f" % c)
        self.benchmarks = (rs+"s",ps+"s",cs+"s")
        self.status = "Status: Benchmark results displayed."
        self.draw()

    def verify(self):
        text = self.value
        key = self.key
        lib = load_rust_cipher_lib()
        buf = create_string_buffer(len(text))
        python = cipher(text,key).decode('cp437').translate(self.ctrl_translation)
        lib.cipher(text,key,buf,len(text), len(key))
        rust = buf[0:len(text)].decode('cp437').translate(self.ctrl_translation)
        if python == rust:
            self.status = "Status: Cipher match verified!"
        else:
            self.status =  "Status: WARNING: ciphers do not match!"
        self.draw()

    def clear(self):
        self.uiprompt = None
        self.benchmarks = None
        self.draw()

    def invalid(self):
        self.status = "Status: ERROR: Invalid menu selection!"
        self.draw()
        

def validateTextbox(text):
    text = text.strip(" ")
    return text

def run_gui(background):
    app = Application(background)
    while True:
        c = background.getkey()
        c = c.upper()
        app.clear()
        if c == "F":
            app.read_file()
        elif c == "I":
            app.new_text()
        elif c == "K":
            app.new_key()
        elif c == "R":
            app.rust_cipher()
        elif c == "P":
            app.python_cipher()
        elif c == "C":
            app.c_cipher()
        elif c == "B":
            app.run_benchmarks()
        elif c == "Q":
            curses.endwin()
            print("Thanks for using the XOR-Cipher App; See you next time!")
            break
        else:
            app.invalid()



if __name__ == "__main__":
    wrapper(run_gui)
