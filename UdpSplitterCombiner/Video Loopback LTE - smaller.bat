@echo off

REM ##### Close existing VLC windows? #####
SET CLOSE_VLC_FIRST=NO

REM ##### VLC path: Portable Version, 64 bit (installed) or 32 bit (installed)? #####
SET VLC=C:\git\gfdmfpga\demos\Support\VideoDemo\VLCPortable\VLCPortable.exe
REM SET VLC="C:\Program Files\VideoLAN\VLC\vlc.exe"
REM SET VLC="C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"

REM ##### Play video on top? (comment line to disable) #####
SET DISPLAY_ON_TOP=--video-on-top


REM ##### Small version #####
SET VIDEO="C:\git\gfdmfpga\demos\Support\VideoDemo\Videos\NI Anthem (smaller).mp4"
REM SET ZOOM="0.5"
REM ##### FullHD version #####
REM SET VIDEO="Videos\NI Anthem (FullHD).ts"
REM SET ZOOM="0.25"

REM ##### UDP ports #####
SET UDP_PORT_TX=49999
SET UDP_PORT_RX=60000


IF "%CLOSE_VLC_FIRST%" == "YES" (
   echo Kill previous running instances
   TASKKILL /F /IM "VLC.exe" > NUL
)

echo Start VLC display instance
start "" %VLC% --zoom=%ZOOM% %DISPLAY_ON_TOP% udp://@:%UDP_PORT_RX%

echo Wait for the receiver window to come up
@timeout /T 2 /nobreak > NUL

echo Start VLC streaming window
start "" %VLC% --repeat %VIDEO% :sout=#std{access=udp{ttl=1},mux=ts,dst=127.0.0.1:%UDP_PORT_TX%}
