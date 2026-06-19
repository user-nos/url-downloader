from download_engine import DownloadEngine
import format_model
import os
import threading
import customtkinter as ctk
from PIL import Image
from CTkMessagebox import CTkMessagebox
from CTkToolTip import CTkToolTip
from tkinter import filedialog

# Creating GUI for downloader script using customtkinter library
# Setting visual theme of customtkinter
ctk.set_appearance_mode( "System" )     # Inherits system's appearance mode Dark/Light
ctk.set_default_color_theme( "dark-blue" )

# Construct main GUI to display
class DownloaderApp( ctk.CTk ):
    def __init__(self):
        super().__init__()

        # Instantiate DownloadEngine
        self.download_engine = DownloadEngine( self.write_to_log )

        # -- Main window --
        self.title( "My Media Downloader V1.0" )
        self.geometry( "+500+300" )
        # self.resizable( False, False )
        self.grid_columnconfigure( 0, weight=1 )

        # -- UI Elements --
        self.downloadtab_row = 0

        # # Scrollabe Frame
        # # Uncomment this part below and change all root elements that
        # # other widgets are attached to this scrollable frame if you want that
        # self.scrollableframe = ctk.CTkScrollableFrame( 
        #     self, 
        #     width=600, 
        #     height=550, 
        #     corner_radius=5, 
        #     fg_color="transparent", 
        #     label_text="URL Downloader",
        #     label_fg_color="gray20",
        #     label_font=ctk.CTkFont( size=20, weight="bold" ),
        #     scrollbar_button_color="gray20"
        # )
        # self.scrollableframe.grid( 
        #     row=0, 
        #     column=0, 
        #     sticky="nsew" 
        # )

        # Title Label
        self.title_frame = TitleFrame(
            self,
            callbackThemetoggle=self.toggle_theme
        )
        self.title_frame.grid( 
            row=0, 
            column=0, 
            padx=10,
            pady=(10, 0), 
            sticky="ew" 
        )
        self.downloadtab_row += 1

        # Tab View
        self.tab_control = ctk.CTkTabview(
            self,
            fg_color="transparent"
        )
        self.tab_control.grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            sticky="nsew"
        )
        self.tab_control._segmented_button.configure(
            font=ctk.CTkFont( size=14 )
        )
        self.download_tab = self.tab_control.add( "Downloader" )
        self.settings_tab = self.tab_control.add( "Settings" )

        # ----------------- Tab 1: Downloader -----------------
        # Save Location Entry + Button with file selection dialog
        self.savelocation_frame = SaveLocationFrame( self.download_tab )
        self.savelocation_frame.grid(
            row=self.downloadtab_row,
            column=0,
            padx=10,
            pady=10,
            sticky="ew"
        )
        self.downloadtab_row += 1

        # Mode Selection Radio buttons (single URL / two URLs)
        self.modetoggle_frame = ModeSelectionFrame( 
            self.download_tab, 
            "Mode Selection", 
            onChangeFunction=self.toggle_mode_selection,
            callback_themetoggle=self.toggle_theme
        )
        self.modetoggle_frame.grid( 
            row=self.downloadtab_row, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="ew"
        )
        self.downloadtab_row += 1

        # Yt-dlp Format selection dropdown
        self.formatselection_frame = OptionMenuFrame(
            self.download_tab,
            label="Select format to download: ",
            options=format_model.YtdlpFormat.OPTIONS
        )
        self.formatselection_frame.grid(
            row=self.downloadtab_row,
            column=0,
            padx=10,
            pady=5,
            sticky="ew"
        )
        self.downloadtab_row += 1

        # Video URL Input
        self.videoinput_frame = EntryFrame( 
            self.download_tab, 
            label="Enter your video url/combined link:", 
            placeholder="https://youtube.com/watch=...",
            errormessage="Error"
        )
        self.videoinput_frame.grid( 
            row=self.downloadtab_row, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="ew" 
        )
        self.downloadtab_row += 1

        # Audio URL Input
        self.audioinput_frame = EntryFrame( 
            self.download_tab,
            label="Enter your audio URL:",
            placeholder="https://cdn.../abc.m3u8",
            errormessage="ERror 2"
        )
        self.audioinput_frame.grid( 
            row=self.downloadtab_row, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="ew" 
        )
        self.downloadtab_row += 1
        self.audioinput_frame.grid_remove()

        # Progress Bar
        self.download_progressbar = ctk.CTkProgressBar( 
            self.download_tab, 
            mode="indeterminate", 
            progress_color="cyan",
            height=20 
        )
        self.download_progressbar.grid( 
            row=self.downloadtab_row, 
            column=0, 
            padx=20, 
            pady=20, 
            sticky="ew" 
        )
        self.downloadtab_row += 1
        self.download_progressbar.grid_remove()

        # Download Button
        self.download_btn = ctk.CTkButton( 
            self.download_tab, 
            text="Download", 
            height=40, 
            command=self.start_download_thread, 
            font=ctk.CTkFont( weight="bold" )
        )
        self.download_btn.grid( 
            row=self.downloadtab_row, 
            column=0, 
            padx=20, 
            pady=20, 
            sticky="ew" 
        )
        self.downloadtab_row += 1

        # Cancel Button
        self.cancel_btn = ctk.CTkButton(
            self.download_tab,
            text="Cancel",
            height=40,
            command=self.trigger_cancel,
            font=ctk.CTkFont( weight="bold" ),
            fg_color="red",
            hover_color="darkred"
        )
        self.cancel_btn.grid(
            row=self.downloadtab_row,
            column=0,
            padx=20,
            pady=20,
            sticky="ew"
        )
        self.downloadtab_row += 1
        self.cancel_btn.grid_remove()

        # Logs Textbox
        self.logs_textbox = ctk.CTkTextbox(
            self.download_tab,
            width=550,
            height=150,
            font=( "Courier", 12 )
        )
        self.logs_textbox.grid(
            row=self.downloadtab_row,
            column=0,
            padx=10,
            pady=10,
            sticky="ew"
        )
        self.downloadtab_row += 1
        self.logs_textbox.configure( state="disabled" ) # Disabled to avoid user inputs
        self.logs_textbox.grid_remove() # Hidden at first, shown after a download is started

        # ----------------- Tab 2: Settings -----------------
        

    # Function to trigger show/hide audio widget based on radio button choice
    def toggle_mode_selection( self, selectedValue ):
        if selectedValue == "single":
            self.audioinput_frame.grid_remove()
            self.formatselection_frame.grid()
        elif selectedValue == "split":
            self.audioinput_frame.grid()
            self.formatselection_frame.grid_remove()

    # Switch theme on button click
    def toggle_theme( self ):
        current_appearance = ctk.get_appearance_mode()
        if current_appearance.lower() == "light":
            ctk.set_appearance_mode( "Dark" )
            self.title_frame.toggle_tooltip_theme()
            self.modetoggle_frame.toggle_tooltip_theme()
        else:
            ctk.set_appearance_mode( "Light" )
            self.title_frame.toggle_tooltip_theme()
            self.modetoggle_frame.toggle_tooltip_theme()
            

    # Trigger cancellation of process when Cancel Button is clicked
    def trigger_cancel( self ):
        # Disable cancel button to avoid double clicks
        self.cancel_btn.configure( state="disabled" )

        # Call DownloadEngine cancellation to stop processes
        self.download_engine.CancelProcess()

    # Safe method to add text to Logs gui textbox
    def write_to_log( self, message ):
        self.after( 0, self.append_to_logs, f"{message}\n" )

    # Actually append text to the logs textbox
    def append_to_logs( self, text ):
        self.logs_textbox.configure( state="normal" )
        self.logs_textbox.insert( "end", text ) # add text at the end 
        self.logs_textbox.see( "end" )  # auto-scroll to the end
        self.logs_textbox.configure( state="disabled" )

    # Empty logs
    def wipe_logs( self ):
        self.logs_textbox.configure( state="normal" )
        self.logs_textbox.delete( "0.0", "end" )
        self.logs_textbox.see( "0.0" )
        self.logs_textbox.configure( state="disabled" )
    
    # Logic behind clicking the "Download" button
    # Start the download logic in a thread so the GUI does not freeze up
    def start_download_thread( self ):
        # Remove the download button so it does not get clicked again
        self.download_btn.grid_remove()
        # Show and start the progress bar
        self.download_progressbar.grid()
        self.download_progressbar.start()
        # Disable entries
        self.videoinput_frame.disable_entry()
        self.audioinput_frame.disable_entry()
        # Show cancel button
        self.cancel_btn.grid()
        # Show Logs textbox
        self.logs_textbox.grid()
        self.wipe_logs()
        
        # Get selected Mode, Video URL & Audio URL
        modeSelected = self.modetoggle_frame.get().strip()
        videoUrl = self.videoinput_frame.get().strip()
        audioUrl = self.audioinput_frame.get().strip()

        # Hide all error messages
        self.videoinput_frame.hide_error_message()
        self.audioinput_frame.hide_error_message()

        # Validate inputs first
        # Error if no url in video field
        if not videoUrl:
            self.videoinput_frame.update_error_message( updatedtext="[ERROR] No URL entered." )
            self.videoinput_frame.show_error_message()
            self.after( 0, self.download_complete( success="", errorfield="video" ) )
            return
        # Error if url does not start with "http:// or https://"
        if not videoUrl.lower().startswith( ( "https://", "http://" ) ):
            self.videoinput_frame.update_error_message( updatedtext="[ERROR] URL entered is not valid." )
            self.videoinput_frame.show_error_message()
            self.after( 0, self.download_complete( success="", errorfield="video" ) )
            return
        # Error if mode chosen is split but no audio url entered
        if modeSelected == "split":
            if not audioUrl:
                self.audioinput_frame.update_error_message( updatedtext="[ERROR] No URL entered." )
                self.audioinput_frame.show_error_message()
                self.after( 0, self.download_complete( success="", errorfield="audio" ) )
                return
            # Error if url does not start with "http:// or https://"
            if not audioUrl.lower().startswith( ( "https://", "http://" ) ):
                self.audioinput_frame.update_error_message( updatedtext="[ERROR] URL entered is not valid." )
                self.audioinput_frame.show_error_message()
                self.after( 0, self.download_complete( success="", errorfield="audio" ) )
                return

        # Start the download process in the background to keep GUI responsive
        threading.Thread( target=self.execute_download, daemon=True ).start()

    # Core Download Logic
    def execute_download( self ):
        download_status = ""
        
        # Get selected Mode, Video URL & Audio URL
        modeSelected = self.modetoggle_frame.get().strip()
        videoUrl = self.videoinput_frame.get().strip()
        audioUrl = self.audioinput_frame.get().strip()
        output_final_destination = self.savelocation_frame.get()
        selected_format = self.formatselection_frame.get().strip()

        # Download the video, audio provided
        if modeSelected == "single":
            # Download video only / combined url
            download_status = self.download_engine.StartDownload( videoUrl=videoUrl, audioUrl=None, formatPreset=selected_format, userOutputPath=output_final_destination )
        elif modeSelected == "split":
            # Download both video url and audio url, and merge them
            download_status = self.download_engine.StartDownload( videoUrl=videoUrl, audioUrl=audioUrl, formatPreset=None, userOutputPath=output_final_destination )

        if download_status == "failed":
            self.after( 0, self.download_complete( success=download_status, errorfield="other" ) )
        else:
            self.after( 0, self.download_complete( success=download_status ) )

    # Logic of what to do after the download is done in the background
    def download_complete( self, success="", errorfield="" ):
        # Remove progress bar and make Download button available again
        self.download_progressbar.stop()
        self.download_progressbar.grid_remove()
        self.download_btn.grid()
        # Enable entries again
        self.videoinput_frame.enable_entry()
        self.audioinput_frame.enable_entry()
        # Hide Cancel Button
        self.cancel_btn.configure( state="normal" )
        self.cancel_btn.grid_remove()

        # Show Error messages if validation failed
        if success == "":
            if errorfield == "both":
                self.videoinput_frame.show_error_message()
                self.audioinput_frame.show_error_message()
            if errorfield == "video":
                self.videoinput_frame.show_error_message()
            if errorfield == "audio":
                self.audioinput_frame.show_error_message()
            if errorfield == "other":
                # Show message box upon completion
                CTkMessagebox(
                    title="Error",
                    message="Something went wrong. Check the logs.",
                    icon="cancel",
                    topmost=True
                )

        if success == "success":
            # Hide error messages if no failed validation for next download
            self.videoinput_frame.hide_error_message()
            self.audioinput_frame.hide_error_message()
            # Show message box upon completion
            CTkMessagebox(
                message="Download successful.",
                icon="check",
                option_1="OK",
                topmost=True
            )

# Construct Title part
class TitleFrame( ctk.CTkFrame ):
    def __init__( self, master, callbackThemetoggle ):
        super().__init__( master )
        self.grid_columnconfigure( 0, weight=1 )
        self.grid_columnconfigure( 1, weight=2 )
        self.grid_columnconfigure( 2, weight=1 )

        self.callback_themetoggle = callbackThemetoggle

        # Left spacer placeholder
        self.title_leftspacer = ctk.CTkFrame(
            self,
            width=35,
            height=1,
            fg_color="transparent"
        )
        self.title_leftspacer.grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=10
        )

        # Main title
        self.title_label = ctk.CTkLabel( 
            self, 
            text="Media Downloader", 
            font=ctk.CTkFont( "Arial", size=20, weight="bold" ) 
        )
        self.title_label.grid( 
            row=0,
            column=1,
            padx=15,
            pady=20,
            sticky="ew" 
        )

        # Theme Toggler button
        # Load icon images
        try:
            self.themetoggleframe_toggleimage = ctk.CTkImage(
                light_image=Image.open( "images/dark_icon.png" ),
                dark_image=Image.open( "images/light_icon.png" ),
                size=( 20, 20 )
            )
        except FileNotFoundError:
            # Fallback to text if image not available
            self.themetoggleframe_toggleimage = None
            print( "Icon images not found, Falling back to text." )

        # Add toggle button
        self.themetoggleframe_togglebutton = ctk.CTkButton(
            self,
            text="" if self.themetoggleframe_toggleimage else "🌓", # Text fallback if no image
            image=self.themetoggleframe_toggleimage,
            width=30,
            height=30,
            fg_color=( "gray80", "gray20" ),
            hover_color=( "gray70", "gray35" ),
            command=self.callback_themetoggle
        )
        self.themetoggleframe_togglebutton.grid(
            row=0,
            column=2,
            padx=15,
            pady=10,
            sticky="e"
        )

        # Add tooltip to theme toggle button
        self.themetoggleframe_togglebutton_tooltip = CTkToolTip(
            self.themetoggleframe_togglebutton,
            message="Light mode",
            delay=0.5
        )

    # Change backgroud of tooltip with theme change as there seem to be a bug about it
    def toggle_tooltip_theme( self ):
        current_appearance = ctk.get_appearance_mode()
        if current_appearance.lower() == "light":
            self.themetoggleframe_togglebutton_tooltip.configure(
                message="Dark mode",
                bg_color="gray86"
            )
        else:
            self.themetoggleframe_togglebutton_tooltip.configure(
                message="Light mode",
                bg_color="gray17"
            )


# Construct Mode selection part
class ModeSelectionFrame( ctk.CTkFrame ):
    def __init__( self, master, title, onChangeFunction, callback_themetoggle ):
        super().__init__( master )
        self.grid_columnconfigure( 0, weight=1 )
        self.frametitle = title
        self.onChangeFunction = onChangeFunction
        self.callback_themetoogle = callback_themetoggle

        self.modeselection_variable = ctk.StringVar( value="single" )

        # Adding a title to the frame
        self.modeselection_title = ctk.CTkLabel( 
            self, 
            text=self.frametitle, 
            fg_color=( "gray70", "gray30" ),
            corner_radius=6,
            font=ctk.CTkFont( weight="bold" )
        )
        self.modeselection_title.grid( 
            row=0, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="ew", 
            columnspan=2 
        )

        # Radioboxes for choice of mode
        self.radiobutton_single = ctk.CTkRadioButton( 
            self, 
            text="Single URL", 
            value="single", 
            variable=self.modeselection_variable, 
            command=self.toggle_mode, 
            fg_color="cyan" 
        )
        self.radiobutton_single.grid( 
            row=1, 
            column=0, 
            padx=20, 
            pady=20, 
            sticky="w" 
        )
        self.radiobutton_single_tooltip = CTkToolTip( 
            self.radiobutton_single,
            message="Uses Yt-dlp in the background to initiate the download."
        )

        self.radiobutton_split = ctk.CTkRadioButton( 
            self, 
            text="Split URL", 
            value="split", 
            variable=self.modeselection_variable, 
            command=self.toggle_mode, 
            fg_color="cyan" 
        )
        self.radiobutton_split.grid( 
            row=1, 
            column=1, 
            padx=20, 
            pady=20, 
            sticky="w" 
        )
        self.radiobutton_split_tooltip = CTkToolTip( 
            self.radiobutton_split,
            message="Uses FFMPEG in the background to get the video and audio, and then merge them together."
        )

    def toggle_mode( self ):
        currentValue = self.get()
        self.onChangeFunction( currentValue )
    
    def get( self ):
        return self.modeselection_variable.get()

    def set( self, value ):
        self.modeselection_variable.set( value )

    # Change backgroud of tooltip with theme change as there seem to be a bug about it
    def toggle_tooltip_theme( self ):
        current_appearance = ctk.get_appearance_mode()
        if current_appearance.lower() == "light":
            self.radiobutton_single_tooltip.configure(
                message="Uses Yt-dlp in the background to initiate the download.",
                bg_color="gray86"
            )
            self.radiobutton_split_tooltip.configure(
                message="Uses FFMPEG in the background to get the video and audio, and then merge them together.",
                bg_color="gray86"
            )
        else:
            self.radiobutton_single_tooltip.configure(
                message="Uses Yt-dlp in the background to initiate the download.",
                bg_color="gray17"
            )
            self.radiobutton_split_tooltip.configure(
                message="Uses FFMPEG in the background to get the video and audio, and then merge them together.",
                bg_color="gray17"
            )

# Construct Entry part
class EntryFrame( ctk.CTkFrame ):
    def __init__( self, master, label, placeholder, errormessage ):
        super().__init__( master )
        self.grid_columnconfigure( 0, weight=1 )
        self.grid_columnconfigure( 1, weight=0 )
        self.grid_columnconfigure( 2, weight=0 )
        self.label = label
        self.entryframe_placeholder = placeholder
        self.entryframe_errormessage = errormessage

        # Label
        self.entryframe_label = ctk.CTkLabel( 
            self, 
            text=self.label 
        )
        self.entryframe_label.grid( 
            row=0, 
            column=0, 
            padx=10, 
            pady=(10,0), 
            sticky="w",
            columnspan=3
        )
        # Input box
        self.entryframe_input = ctk.CTkEntry( 
            self, 
            width=550, 
            placeholder_text=self.entryframe_placeholder 
        )
        self.entryframe_input.grid( 
            row=1, 
            column=0, 
            padx=( 10, 5 ), 
            pady=10, 
            sticky="ew" 
        )

        # Delete button for entry
        # Load icon image
        try:
            self.entryframe_deleteimage = ctk.CTkImage(
                light_image=Image.open( "images/delete_icon.png" ),
                dark_image=Image.open( "images/delete_icon.png" ),
                size=( 20, 20 )
            )
        except FileNotFoundError:
            # Fallback to text if image not available
            self.entryframe_deleteimage = None
            print( "Icon images not found, Falling back to text." )

        # Add delete button
        self.entryframe_deletebtn = ctk.CTkButton(
            self,
            text="" if self.entryframe_deleteimage else "✖", # Text fallback if no image
            image=self.entryframe_deleteimage,
            width=30,
            height=30,
            command=self.empty_entry,
            fg_color="darkred",
            hover_color="red"
        )
        self.entryframe_deletebtn.grid(
            row=1,
            column=1,
            padx=( 0, 5 ),
            pady=10,
            sticky="e"
        )

        # Paste button for entry
        # Load icon image
        try:
            self.entryframe_pasteimage = ctk.CTkImage(
                light_image=Image.open( "images/paste_icon.png" ),
                dark_image=Image.open( "images/paste_icon.png" ),
                size=( 20, 20 )
            )
        except FileNotFoundError:
            # Fallback to text if image not available
            self.entryframe_pasteimage = None
            print( "Icon images not found, Falling back to text." )

        # Add paste button
        self.entryframe_pastebtn = ctk.CTkButton(
            self,
            text="" if self.entryframe_pasteimage else "⎘", # Text fallback if no image
            image=self.entryframe_pasteimage,
            width=30,
            height=30,
            command=self.paste_text
        )
        self.entryframe_pastebtn.grid(
            row=1,
            column=2,
            padx=( 0, 10 ),
            pady=10,
            sticky="e"
        )

        # Add Error label here
        self.entryframe_error = ctk.CTkLabel(
            self,
            text=self.entryframe_errormessage,
            text_color="red",
            font=ctk.CTkFont( weight="bold" )
        )
        self.entryframe_error.grid(
            row=2,
            column=0,
            padx=10,
            pady=10,
            sticky="ew",
            columnspan=3
        )
        self.entryframe_error.grid_remove()

    # Get Entry/Input value
    def get( self ):
        return self.entryframe_input.get()
    
    # Delete the entry/input entirely
    def delete( self ):
        self.entryframe_input.delete( 0, ctk.END )

    # Disable entry
    def disable_entry( self ):
        self.entryframe_input.configure( state="disabled" )

    # Enable the entry
    def enable_entry( self ):
        self.entryframe_input.configure( state="normal" )

    # Update error message label
    def update_error_message( self, updatedtext ):
        self.entryframe_errormessage = updatedtext
        self.entryframe_error.configure( text=self.entryframe_errormessage )

    # Show Error message label
    def show_error_message( self ):
        self.entryframe_error.grid()
        self.configure( border_width=2, border_color="red" )

    # Hide Error message label
    def hide_error_message( self ):
        self.entryframe_error.grid_remove()
        self.configure( border_width=0, border_color=( "gray70", "gray10" ) )

    # Delete content in entry box
    def empty_entry( self ):
        self.entryframe_input.delete( 0, "end" )

    # Paste text into entry box from clipboard
    def paste_text( self ):
        try:
            # Get text from clipboard
            clipboard_text = self.clipboard_get()
            
            if clipboard_text:
                # Clear current entry box first
                self.empty_entry()
                # Insert text into entry box
                self.entryframe_input.insert( 0, clipboard_text.strip() )
        
        except Exception as e:
            return


# Construct Yt-dlp format selection frame
class OptionMenuFrame( ctk.CTkFrame ):
    def __init__( self, master, label, options ):
        super().__init__( master )
        self.grid_columnconfigure( 0, weight=1 )
        self.grid_columnconfigure( 1, weight=1 )
        self.label = label
        self.options = options

        self.optionsmenu_variable = ctk.StringVar( value=format_model.YtdlpFormat.OPTIONS[0] )

        # Label
        self.optionmenuframe_label = ctk.CTkLabel( 
            self, 
            text=self.label 
        )
        self.optionmenuframe_label.grid( 
            row=0, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="w" 
        )

        # Options Menu (dropdown menu)
        self.optionmenuframe_optionsmenu = ctk.CTkOptionMenu(
            self,
            values=self.options,
            variable=self.optionsmenu_variable
        )
        self.optionmenuframe_optionsmenu.grid(
            row=0,
            column=1,
            padx=10,
            pady=5,
            sticky="ew"
        )

    # Get the selected value of the dropdown
    def get( self ):
        return self.optionsmenu_variable.get()
        

# Construct save location input, button and dialog
class SaveLocationFrame( ctk.CTkFrame ):
    def __init__( self, master ):
        super().__init__( master )
        self.grid_columnconfigure( 0, weight=5 )
        self.grid_columnconfigure( 1, weight=1 )
        self.frametitle = "Save Path Location"

        # get a default location
        self.defaultlocation = DownloadEngine.GetDownloadsFolderPath()

        # Adding a title to the frame
        self.savelocationframe_title = ctk.CTkLabel( 
            self, 
            text=self.frametitle, 
            fg_color=( "gray70", "gray30" ), 
            corner_radius=6,
            font=ctk.CTkFont( weight="bold" )
        )
        self.savelocationframe_title.grid( 
            row=0, 
            column=0, 
            padx=10, 
            pady=10, 
            sticky="ew", 
            columnspan=6
        )

        # Adding entry box to display path
        self.savelocationframe_input = ctk.CTkEntry(
            self
        )
        self.savelocationframe_input.insert( 0, self.defaultlocation )
        self.savelocationframe_input.configure( state="readonly" )
        self.savelocationframe_input.grid(
            row=1,
            column=0,
            padx=( 10, 0 ),
            pady=10,
            sticky="ew"
        )

        # Adding button to open file selection dialog
        self.savelocationframe_browsebutton = ctk.CTkButton(
            self,
            text="Browse",
            command=self.select_path
        )
        self.savelocationframe_browsebutton.grid(
            row=1,
            column=1,
            padx=( 0, 10 ),
            pady=10,
            sticky="ew"
        )

    # Get value in the input box for the path
    def get( self ):
        return self.savelocationframe_input.get()

    # Open file dialog to choose path
    def select_path( self ):
        # Get current directory selected from the entry box
        current_directory = self.savelocationframe_input.get()
        # Open folder selection dialog at the current chosen folder
        selected_path = filedialog.askdirectory( initialdir=current_directory )
        if selected_path:
            self.savelocationframe_input.configure( state="normal" )
            self.savelocationframe_input.delete( 0, "end" )
            self.savelocationframe_input.insert( 0, os.path.normpath( selected_path ) )
            self.savelocationframe_input.configure( state="readonly" )

# Construct Settings Frame
class SettingsFrame( ctk.CTkFrame ):
    def __init__( self, master ):
        super().__init__( master )
        self.grid_columnconfigure( 0, weight=1 )

        