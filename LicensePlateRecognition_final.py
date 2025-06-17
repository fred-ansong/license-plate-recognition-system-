##############################################################################################
#Group 2: Frederick Ansong, Joshua Palma, Cameren Sudduth
#Date: 5/1/2025
#Description: This code is supposed to model our project idea for a License Plate Recognition
# system for license plates reported for AMBER Alerts. The program uses tesseract OCR to detect
# text optically. The code takes the scanned text and runs it through a txt file to see if it
# matches any of the license plates we have written for the example AMBER Alert database. If
# a match is found it gives a pop up of the location of the camera that scanned it and turns
# the X mark next to the license plate into a check mark. The video is also shown inside the
# GUI live.
##############################################################################################
# Imported Libraries
from tkinter import *
from tkinter import messagebox
import threading
import cv2
from PIL import Image, ImageTk  
import pytesseract
import time

# Camera Setup
vid = cv2.VideoCapture(0) #selects default camera
width = 200
height = 200
vid.set(cv2.CAP_PROP_FRAME_WIDTH, width) 
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height) 

# If the camera isnt running shows error message and stops code.
if not vid.isOpened():
    print("Error: Could not open video device.")
    exit()
    
# Global variables for OCR
latest_text = "" #initialized variable storing scanned text
ocr_lock = threading.Lock() #creates a seperate thread that avoids freezing the GUI

last_ocr_time = time.time() # reduces run time on ocr to reduce cpu load
custom_config = r'--oem 3 --psm 6' # settings for text interpretation
match_found = False # shows whether license plate has been found or not

# Read the license plates from a file
with open("plates.txt", "r") as f:
    plates_list = f.read().splitlines() # reads each line of the file individually

class GUITest(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master # initializes main window
        
    
    def setup(self):
        #window setup
        self.master.geometry("900x650") # main window size
        self.master.title("Lisence Plate Recognition") # window title
        
        # Outer Outer Frame setup
        self.OuterOuterFrame = Frame(self.master, borderwidth = 4, width=890, height=640 ,relief= 'solid')
        self.OuterOuterFrame.grid_propagate(False)
        self.OuterOuterFrame.grid(row=0,column=0, padx=5,pady=5)

        # Configure rows and columns to handle vertical spacing
        self.OuterOuterFrame.grid_rowconfigure(0, weight=0)  # Logo
        self.OuterOuterFrame.grid_rowconfigure(1, weight=1)  # Spacer row
        self.OuterOuterFrame.grid_rowconfigure(2, weight=0)  # Bottom row for frames
        self.OuterOuterFrame.grid_columnconfigure(0, weight=1)
        self.OuterOuterFrame.grid_columnconfigure(1, weight=1)

        # frame for video and license plate text
        self.Textframe = Frame(self.OuterOuterFrame, borderwidth = 3, relief= 'solid', width = 330, height=360)
        self.Textframe.grid_propagate(False)
        self.Textframe.grid(row=2,column=0, sticky="e"+"s", padx=20, pady=50)
        self.Videoframe = Frame(self.OuterOuterFrame, borderwidth = 3, relief= 'solid', width =500, height=360)
        self.Videoframe.grid_propagate(False)
        self.Videoframe.grid(row=2,column=0,sticky="w"+"s", padx= 20, pady=50)
        
        # License Plates Text
        self.LicensePlateTitle = Label(self.Textframe, text = 'License Plates', font=('utopia',30))
        self.LicensePlateTitle.grid(padx=30)
        self.FXM0222 = Label(self.Textframe, text = 'FXM 0222  X', font=('utopia',30))
        self.FXM0222.grid()
        self.LHD8448 = Label(self.Textframe, text = 'LHD 8448  X', font=('utopia',30))
        self.LHD8448.grid()
        self.VFF440G = Label(self.Textframe, text = 'VFF 440G  X', font=('utopia',30))
        self.VFF440G.grid()
        self.ABC234 = Label(self.Textframe, text = 'ABC 234  X', font=('utopia',30))
        self.ABC234.grid()
       
        #Logo Image
        self.Logo1 = PhotoImage(file="/home/pi/Freshman Project /Logo.png").subsample(1)
        Label(self.OuterOuterFrame, image=self.Logo1).grid(row=0,column=0, sticky='W', padx=200)

        #Video Frame setup
        self.Videoframein = Label(self.Videoframe)
        self.Videoframein.grid()
        self.open_camera()

    def open_camera(self):
        global latest_text, last_ocr_time, match_found 
        
        
        # Capture frame-by-frame
        ret, frame = vid.read()
        
        # If frames arent captured it shows us
        if not ret:
            print("Failed to capture frame")
            return
        # sets captured frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # reduces noise around text making it more accurate
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Lets opencv choose the best threshold to differentiate text from background
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # keeps the code from running too fast by checking if a second has passed since a match hasnt been found
        if time.time() - last_ocr_time > 1.0 and not match_found:
            #runs tesseract ocr on the image to extract words
            data = pytesseract.image_to_data(thresh, config=custom_config, output_type=pytesseract.Output.DICT)

            #Shows us the scanned text and the confidence with the accuracy of the text
            print("\n--- Detected Words ---")
            lines = {}
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                try:
                    conf = int(float(data['conf'][i]))
                except:
                    conf = -1

                if text and conf > 5:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

                    # Draw rectangle and text
                    cv2.rectangle(thresh, (x, y), (x + w, y + h), (0, 0, 0), 2)
                    cv2.putText(thresh, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                    print(f"Detected: '{text}' | Confidence: {conf}")

                    # Group text by line height (approximate)
                    line_key = y // 20
                    if line_key not in lines:
                        lines[line_key] = []
                    lines[line_key].append(text)

            # Reconstruct full lines and check against plates
            for line_texts in lines.values():
                full_line = ''.join(line_texts).lower().replace(" ", "")
                print(f' This is the full line:{full_line}')
                print(f"Reconstructed Line: {full_line}")

                # For the amount of license plates in the list the extracted text is cycled through to find a match
                for plate in plates_list:
                    if plate.strip().lower().replace(" ", "") == full_line:
                        print(f"? Match found for plate: {plate}")
                        # Checks if license plate was found and if it was updates X to ? 
                        if full_line == 'abc234':
                            self.ABC234.config(text = 'ABC 234 ?', font=('utopia',30))
                            
                            #Plate_Dected_Frame
                            Plate_Detected_Window = Toplevel(self.Textframe)
                            Plate_Detected_Window.title("Plate Detected")
                            Plate_Detected_Window.geometry("500x100+200+300")
                            
                            Plate_Detected_Window_Message = Label(Plate_Detected_Window, text = "The lisence plate 'ABC 234' has been found at 7502 Fondren Rd.")
                            Plate_Detected_Window_Message.pack()
                            
                            time.sleep(5)
                            
                            Plate_Detected_Window.after(5000, lambda: Plate_Detected_Window.destroy())
                            
                        if full_line == 'fxm0222':
                            self.FXM0222.config(text = 'FXM 0222  ?', font=('utopia',30))
                            
                            #Plate_Dected_Frame
                            Plate_Detected_Window = Toplevel(self.Textframe)
                            Plate_Detected_Window.title("Plate Detected")
                            Plate_Detected_Window.geometry("500x100+200+300")
                            
                            Plate_Detected_Window_Message = Label(Plate_Detected_Window, text = "The lisence plate 'FXM 0222' has been found at 7502 Fondren Rd.")
                            Plate_Detected_Window_Message.pack()
                            
                            time.sleep(5)
                            
                            Plate_Detected_Window.after(5000, lambda: Plate_Detected_Window.destroy())
                            
                        if full_line == 'lhd8448':
                            self.LHD8448.config(text = 'LHD 8448 ?', font=('utopia',30))
                            
                            #Plate_Dected_Frame
                            Plate_Detected_Window = Toplevel(self.Textframe)
                            Plate_Detected_Window.title("Plate Detected")
                            Plate_Detected_Window.geometry("500x100+200+300")
                            
                            Plate_Detected_Window_Message = Label(Plate_Detected_Window, text = "The lisence plate 'LHD 8448' has been found at 7502 Fondren Rd.")
                            Plate_Detected_Window_Message.pack()
                            
                            time.sleep(5)
                            
                            Plate_Detected_Window.after(5000, lambda: Plate_Detected_Window.destroy())
                            
                        if full_line == 'vff440g':
                            self.VFF440G.config(text = 'VFF 440G ?', font=('utopia',30))
                            
                            #Plate_Dected_Frame
                            Plate_Detected_Window = Toplevel(self.Textframe)
                            Plate_Detected_Window.title("Plate Detected")
                            Plate_Detected_Window.geometry("500x100+200+300")
                            
                            Plate_Detected_Window_Message = Label(Plate_Detected_Window, text = "The lisence plate 'VFF 440G' has been found at 7502 Fondren Rd.")
                            Plate_Detected_Window_Message.pack()
                            
                            time.sleep(5)
                            
                            Plate_Detected_Window.after(5000, lambda: Plate_Detected_Window.destroy())
                        
        
                        
                        
                        
            #updates ocr time
            last_ocr_time = time.time()
        #Updates whats shown in the GUI video frame
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.Videoframein.imgtk = imgtk
        self.Videoframein.configure(image=imgtk)
        # calls open camera function every 30 frames
        self.master.after(30, self.open_camera)

      
# Main Program Loop
window = Tk()
t = GUITest(window)
t.setup()
window.mainloop()

