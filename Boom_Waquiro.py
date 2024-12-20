# Import a library of functions called 'pygame'
import pygame
import pygame.midi
import random
import sys
import os

from xml.etree import ElementTree

import argparse
import subprocess

baseDir = os.getcwd()
parser = argparse.ArgumentParser(description='Import a musicxml song for a waterfall')
parser.add_argument('--music', dest='music', help='file path, .musicxml')
parser.add_argument('--folder', dest='folder', default = baseDir, help='folder containing music')
parser.add_argument('--voice', dest='voices', help='comma separated list of voices to display')
parser.add_argument('--accompany', dest='accompanyParts', help='comma separted list of parts to use for midi accompaniment')
parser.add_argument('--octaves', dest='octaves', default='1', help='number of octaves to show')
args = parser.parse_args()

PI = 3.14159265358
debugScore = True

"""
 Colors needing to be defined.
"""
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]

RED = [255, 0, 40]
REDORANGE = [255, 95, 0]
ORANGE = [255, 165, 0]
ORANGEYELLOW = [255, 215, 0]
YELLOW = [255, 255, 0]
LIGHTGREEN = [144, 245, 0]
GREEN = [18, 173, 42]
DARKGREEN = [40, 160, 120]
BLUE = [0, 0, 255]
VIOLET = [48, 16, 180]
LAVENDER = [129, 0, 127]
PINK = [210, 15, 192]

GRAY = [200, 200, 200]

color_list = [
    RED,
    REDORANGE,
    ORANGE,
    ORANGEYELLOW,
    YELLOW,
    LIGHTGREEN,
    GREEN,
    DARKGREEN,
    BLUE,
    VIOLET,
    LAVENDER,
    PINK
    ]

toneLookup = {
    "C" : 0,
    "D" : 2,
    "E" : 4,
    "F" : 5,
    "G" : 7,
    "A" : 9,
    "B" : 11
    }

# ---------
# Class for defining the notes that will come down the screen
# ---------
LOWEST_NOTE = 12*3
HIGHEST_NOTE = 12*5

class MusicNote():
    # This is a class representing a musical note.

    def __init__(self):
        self.pitch = 0
        self.octave = 0
        self.length = 0
        self.noteSize = NOTESIZE
        self.name = ""

class SixteenthNote(MusicNote):
    def __init__(self, pitch, octave, length, dotted=False):
        self.pitch = pitch
        self.octave = octave
        self.length = length
        self.noteSize = NOTESIZE
        self.width = 2
        self.dotted = dotted

    def draw(self, pos, color=BLACK):
        x = pos[0]
        y = pos[1]
        ns = self.noteSize
        w = self.width
        pygame.draw.circle(screen, color, [x,y], ns)
        pygame.draw.line(screen, color, [x+ns-w+1,y], [x+ns-w+1,y-4*ns], w)
        # First flag
        flagRect = pygame.Rect((x+ns-w+1, y-5*ns), (1.25*ns, 2*ns))
        pygame.draw.arc(screen, color, flagRect, PI, 1.5*PI, w)
        flagRect = pygame.Rect((x+ns-w, y-3*ns), (1.25*ns, 2*ns))
        pygame.draw.arc(screen, color, flagRect, 0, 0.5*PI, w)
        # Second flag
        flagRect = pygame.Rect((x+ns-w+1, y-4*ns), (1.25*ns, 2*ns))
        pygame.draw.arc(screen, color, flagRect, PI, 1.5*PI, w)
        flagRect = pygame.Rect((x+ns-w, y-2*ns), (1.25*ns, 2*ns))
        pygame.draw.arc(screen, color, flagRect, 0, 0.5*PI, w)
        if self.dotted:
            pygame.draw.circle(screen, color, [x+w+5,y], 5)

class EighthNote(MusicNote):
    def __init__(self, pitch, octave, length, dotted=False):
        self.pitch = pitch
        self.octave = octave
        self.length = length
        self.noteSize = NOTESIZE
        self.width = 2
        self.dotted = dotted

    def draw(self, pos, color=BLACK):
        x = pos[0]
        y = pos[1]
        ns = self.noteSize
        w = self.width
        pygame.draw.circle(screen, color, [x,y], ns)
        pygame.draw.line(screen, color, [x+ns-w+1,y], [x+ns-w+1,y-4*ns], w)
        flagRect = pygame.Rect((x+ns-w+1, y-5*ns), (1.25*ns, 2*ns))
        pygame.draw.arc(screen, color, flagRect, PI, 1.5*PI, w)
        flagRect = pygame.Rect((x+ns-w, y-3*ns), (1.25*ns, 2*ns))
        pygame.draw.arc(screen, color, flagRect, 0, 0.5*PI, w)
        if self.dotted:
            pygame.draw.circle(screen, color, [x+w+5,y], 5)

class QuarterNote(MusicNote):
    def __init__(self, pitch, octave, length, dotted=False):
        self.pitch = pitch
        self.octave = octave
        self.length = length
        self.noteSize = NOTESIZE
        self.width = 2
        self.dotted = dotted

    def draw(self, pos, color=BLACK):
        x = pos[0]
        y = pos[1]
        ns = self.noteSize
        w = self.width
        pygame.draw.circle(screen, color, [x,y], ns)
        pygame.draw.line(screen, color, [x+ns-w+1,y], [x+ns-w+1,y-4*ns], w)
        if self.dotted:
            pygame.draw.circle(screen, color, [x+w+5,y], 5)

class HalfNote(MusicNote):
    def __init__(self, pitch, octave, length, dotted=False):
        self.pitch = pitch
        self.octave = octave
        self.length = length
        self.noteSize = NOTESIZE
        self.width = 2
        self.dotted = dotted

    def draw(self, pos, color=BLACK):
        x = pos[0]
        y = pos[1]
        ns = self.noteSize
        w = self.width
        pygame.draw.circle(screen, color, [x,y], ns, w)
        pygame.draw.line(screen, color, [x+ns-w+1,y], [x+ns-w+1,y-4*ns], w)
        if self.dotted:
            pygame.draw.circle(screen, color, [x+ns+ns//2,y],ns//4)

class Song():
    def __init__(self, tempo, playAlongNotes, accompanyNotes):
        self.tempo = tempo
        # Array of Note elements
        self.playAlong = playAlongNotes
        # Array of Note elements
        self.accompaniment = accompanyNotes

class AppMode():
    done = False
    doQuit = False
    def handleEvent(this, event):
        if event.type == pygame.QUIT:  # If user clicked close
            done = True   # Flag that we are done so we exit this loop
            doQuit = True
    def updateScreen(this):
        pass
    def doUpdate(this):
        this.updateScreen()

class SongSelector(AppMode):
    songList = []
    songSelect = 0
    topRow = 0
    visibleRows = 10
    curPath = ""

    def loadSongList(this, folderPath):
        this.curPath = folderPath
        this.songList = []
        this.topRow = 0
        this.songSelect = 0
        tempList = os.listdir(folderPath)
        # Find all the folders first, including the up directory
        this.songList.append(":..:")
        for f in tempList:
            if not os.path.isfile(os.path.join(folderPath, f)):
                this.songList.append(":"+f+":")
        # Rescan keeping only files with suffix .musicxml
        for f in tempList:
            if os.path.isfile(os.path.join(folderPath, f)) and f.endswith('.musicxml'):
                this.songList.append(f)

    def updateScreen(this):
        # Set the screen background
        screen.fill(BLACK)

        # Clear the window space for the list
        WIDTH = screen.get_width()
        HEIGHT = screen.get_height()
        LINEHEIGHT = 18
        PANEHEIGHT = LINEHEIGHT * (this.visibleRows+1)
        PANEWIDTH = 600
        paneLeft = (WIDTH - PANEWIDTH) // 2
        paneTop = (HEIGHT - PANEHEIGHT) // 2
        pygame.draw.rect(screen, WHITE, pygame.Rect(paneLeft, paneTop, PANEWIDTH, PANEHEIGHT))
        for row in range(this.topRow, this.topRow+this.visibleRows):
            if (row == this.songSelect):
                prefix = "-> "
                color = RED
            else:
                prefix = "  "
                color = BLACK
            if row < len(this.songList):
                songText = create_text(prefix + this.songList[row], nameFonts, LINEHEIGHT, color)
                screen.blit(songText, (paneLeft+10, paneTop + (row-this.topRow+0.5)*LINEHEIGHT))
        pygame.display.flip()

    def handleEvent(this, event):
        redraw = False
        # Deal with higher level events
        super().handleEvent(event)
        if event.type == pygame.KEYDOWN:
            # Select the current song or folder
            if event.key == pygame.K_RETURN:
                # See if it is a directory.
                if this.songList[this.songSelect].startswith(':'):
                    redraw = True
                    dirName = this.songList[this.songSelect][1:-1]
                    pathDir = os.path.join(this.curPath, dirName)
                    this.loadSongList(pathDir)
                else:
                    redraw = False
                    controller.stack.append(this)
                    controller.active = SongStartup()
                    controller.active.initialize(this.curPath, this.songList[this.songSelect])

            elif event.key == pygame.K_ESCAPE:
                this.done = True
            elif event.key in [pygame.K_UP, pygame.K_j]:
                redraw = True
                this.songSelect = max(this.songSelect - 1, 0)
                if this.songSelect < this.topRow:
                    this.topRow = this.songSelect
            elif event.key in [pygame.K_DOWN, pygame.K_k]:
                redraw = True
                this.songSelect = min(this.songSelect + 1, len(this.songList)-1)
                if this.songSelect >= this.topRow + this.visibleRows:
                    this.topRow = this.songSelect-this.visibleRows+1
        if redraw:
            this.doUpdate()


class SongStartup(AppMode):
    topRow = 0
    curRow = 0
    visibleRows = 6
    tempo = 80
    octaves = 2

    def initialize(this, path, song):
        songPath = os.path.join(path, song)
        this.players = []
        this.accompany = []
        this.playNotes = []
        startTempo = 0

        # Import the music data
        this.mxml = ElementTree.parse(songPath).getroot()

        # Find the title
        titleTypes = ["work/work-title", "movement-title"]
        this.songTitle = "Untitled"
        for titleType in titleTypes:
            workTitle = this.mxml.find(titleType)
            print(titleType, workTitle)
            if workTitle is not None:
                this.songTitle = workTitle.text
                break
            
        if (this.mxml.tag == 'score-partwise'):
            # This structure has multiple parts. Each part has multiple measures.
            # Find the list of parts.
            partlist = this.mxml.find("part-list")
            this.parts = []
            if partlist is not None:
                # Find the part we are looking for.
                for part in partlist.iter("score-part"):
                    partID = part.get("id")
                    partName = part.find("part-name")
                    print(partID, partName.text)
                    this.parts.append([partID, "" if partName is None or partName.text is None else partName.text])
            for part in this.mxml.iter("part"):
                # Work through each measure in the part.
                timeCode = 0.0
                partCode = part.get("id")
                for measure in part.iter("measure"):
                    # Within each measure, go through each element.
                    # Some elements are about attributes.
                    # Others are notes, rests or other timing items.
                    for musicUnit in measure:
                        if musicUnit.tag == "direction":
                            # Tempo is hidden in direction including "sound"
                            soundFeature = musicUnit.find("sound")
                            if soundFeature is not None and soundFeature.get("tempo") is not None:
                                tempo = int(soundFeature.get("tempo"))
                                if startTempo == 0:
                                    startTempo = tempo
                                    this.tempo = tempo
        this.updatePlayerParts()

    def updatePlayerParts(this):
        this.playNotes = []
        this.noteCount = dict()
        if (this.mxml.tag == 'score-partwise'):
            # Using the parts identified, look for measures belonging to that part.
            for part in this.mxml.iter("part"):
                # Work through each measure in the part.
                timeCode = 0.0
                partCode = part.get("id")
                for measure in part.iter("measure"):
                    # Within each measure, go through each element.
                    # Some elements are about attributes.
                    # Others are notes, rests or other timing items.
                    for musicUnit in measure:
                        if musicUnit.tag == "note":
                            tieInfo = musicUnit.find("tie")
                            if tieInfo is not None:
                                typeOfTie = tieInfo.get("type")
                            else:
                                typeOfTie = "none"

                            # If it is not a rest, then pull out the pitch information.
                            if musicUnit.find("rest") is None and (tieInfo is None or typeOfTie == "start"):
                                # What note is played by pitch?
                                pitchInfo = musicUnit.find("pitch")
                                octave = pitchInfo.find("octave")
                                step = pitchInfo.find("step")
                                alter = pitchInfo.find("alter")
                                # What type of note?
                                symbol = musicUnit.find("type").text

                                # Translate to standard information
                                tone = toneLookup.get(step.text)
                                adjust = 0
                                if alter is not None:
                                    adjust = int(alter.text)
                                    tone = tone + adjust
                                if octave is None:
                                    octave = 4
                                else:
                                    octave = int(octave.text)

                                # Standardize in case sharps or flats shift to different octave
                                noteIndex = 12*octave+tone
                                octave = noteIndex // 12
                                tone = noteIndex % 12

                                if partCode in this.players:
                                    adjustedTone = 12*octave + tone
                                    while adjustedTone > HIGHEST_NOTE:
                                        octave = octave - 1
                                        adjustedTone = 12*octave + tone
                                    while adjustedTone < LOWEST_NOTE:
                                        octave = octave + 1
                                        adjustedTone = 12*octave + tone
                                    theNote = Note(tone, adjust, octave, symbol, timeCode, 1)
                                    this.playNotes.append(theNote)
                                    newCnt = this.noteCount.get(adjustedTone, 0) + 1
                                    this.noteCount[adjustedTone] = newCnt

        elif (this.mxml.tag == 'score-timewise'):
            # This structure has multiple measures. Each measure has multiple parts.
            pass
        else:
            print("Score structure not recognized.")

        # Sort the notes into time-based ordering.
        this.playNotes.sort(key = lambda note : note.octave)
        this.playNotes.sort(key = lambda note : note.tone)

    def updateScreen(this):
        # Set the screen background
        screen.fill(WHITE)

        # Clear the window space for the list
        WIDTH = screen.get_width()
        HEIGHT = screen.get_height()

        # Draw the title of the song
        titleText = create_text(this.songTitle, nameFonts, 36, GRAY)
        screen.blit(titleText,
                    ((WIDTH - titleText.get_width()) // 2, HEIGHT // 4))

        # Draw BPM
        bpmText = create_text(str(this.tempo) + " bpm", nameFonts, 24, GRAY)
        screen.blit(bpmText,
                    ((WIDTH - bpmText.get_width()) // 2, HEIGHT // 4 + 36))

        # Draw the line where we should play.
        pygame.draw.line(screen, BLACK, [0,FLASHLINE], [WIDTH,FLASHLINE], 5)

        # Process each note that should appear on the screen.
        if this.octaves=='1':
            refPos = 100
            spacing = (WIDTH-200) // 12
        else:
            refPos = WIDTH//2
            spacing = (WIDTH-200) // 24
        noteList = list(this.noteCount.keys())
        noteList.sort()
        for note in noteList:
            octave = note // 12
            tone = note % 12
            x = refPos + (note-48)*spacing
            noteName = diatonicNames[tone] + str(octave)
            theNote = Note(tone, 0, octave, "Q", 0, 1)
            theNote.draw(screen, [x, STARTLINE], 0)

            cnt = this.noteCount[note]
            pos = [x, STARTLINE+20]

            cntText = create_text(str(cnt), nameFonts, 18, WHITE)
            cntTextShadow = create_text(str(cnt), nameFonts, 18, BLACK)
            screen.blit(cntTextShadow,
                (pos[0] - cntText.get_width() // 2 - 1, pos[1] - cntText.get_height() // 2 - 1))
            screen.blit(cntTextShadow,
                (pos[0] - cntText.get_width() // 2 + 1, pos[1] - cntText.get_height() // 2 - 1))
            screen.blit(cntTextShadow,
                (pos[0] - cntText.get_width() // 2 - 1, pos[1] - cntText.get_height() // 2))
            screen.blit(cntTextShadow,
                (pos[0] - cntText.get_width() // 2 + 1, pos[1] - cntText.get_height() // 2))
            screen.blit(cntTextShadow,
                (pos[0] - cntText.get_width() // 2 - 1, pos[1] - cntText.get_height() // 2 + 1))
            screen.blit(cntTextShadow,
                (pos[0] - cntText.get_width() // 2 + 1, pos[1] - cntText.get_height() // 2 + 1))
            screen.blit(cntText,
                (pos[0] - cntText.get_width() // 2, pos[1] - cntText.get_height() // 2))

        LINEHEIGHT = 18
        PANEHEIGHT = LINEHEIGHT * (this.visibleRows+4)
        PANEWIDTH = 600

        paneLeft = (WIDTH - PANEWIDTH) // 2
        paneTop = (HEIGHT - PANEHEIGHT) // 2
        pygame.draw.rect(screen, WHITE, pygame.Rect(paneLeft, paneTop, PANEWIDTH, PANEHEIGHT))
        instrText = create_text("Press Key to Toggle: [P]layer, [A]ccompaniment", nameFonts, LINEHEIGHT, BLACK)
        screen.blit(instrText, (paneLeft+5, paneTop + 0.5*LINEHEIGHT))

        for row in range(this.topRow, this.topRow+this.visibleRows):
            if (row == this.curRow):
                prefix = "-> "
                color = RED
            else:
                prefix = "  "
                color = BLACK
            if row < len(this.parts):
                playCode = "["
                partID = this.parts[row][0]
                playCode = playCode + ("P " if partID in this.players else "  ")
                playCode = playCode + ("A]" if partID in this.accompany else " ]")
                playText = create_text(prefix + playCode, nameFonts, LINEHEIGHT, color)
                screen.blit(playText, (paneLeft+10, paneTop + (row-this.topRow+2)*LINEHEIGHT))
                partText = create_text(" ".join(this.parts[row]), nameFonts, LINEHEIGHT, color)
                screen.blit(partText, (paneLeft+80, paneTop + (row-this.topRow+2)*LINEHEIGHT))
        pygame.display.flip()

    def handleEvent(this, event):
        redraw = False
        # Deal with higher level events
        super().handleEvent(event)
        if event.type == pygame.KEYDOWN:
            # Play the current song or folder
            if event.key == pygame.K_RETURN:
                redraw = False
                controller.active = SongPlayer()
                controller.active.initialize(this.mxml, this.players, this.accompany, this.octaves, this.songTitle, this.tempo)

            # Backup a level and choose a different song
            elif event.key == pygame.K_ESCAPE:
                redraw = False
                controller.active = controller.stack.pop()

            elif event.key == pygame.K_p:
                partID = this.parts[this.curRow][0]
                if partID in this.players:
                    this.players.remove(partID)
                else:
                    this.players.append(partID)
                this.updatePlayerParts()
                redraw = True

            elif event.key == pygame.K_a:
                partID = this.parts[this.curRow][0]
                if partID in this.accompany:
                    this.accompany.remove(partID)
                else:
                    this.accompany.append(partID)
                redraw = True

            elif event.key in [pygame.K_UP, pygame.K_j]:
                redraw = True
                this.curRow = max(this.curRow - 1, 0)
                if this.curRow < this.topRow:
                    this.topRow = this.curRow

            elif event.key in [pygame.K_DOWN, pygame.K_k]:
                redraw = True
                this.curRow = min(this.curRow + 1, len(this.parts)-1)
                if this.curRow >= this.topRow + this.visibleRows:
                    this.topRow = this.curRow-this.visibleRows+1

            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                this.tempo = this.tempo + 4
            elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                this.tempo = this.tempo - 4
        if redraw:
            this.doUpdate()


class SongPlayer(AppMode):
    def initialize(this, mxml, players, accompany, octaves, title, bpm):
        this.playerParts = players
        this.accompanyParts = accompany
        this.playNotes = []
        this.accompaniment = []
        this.octaves = octaves
        this.songTitle = title
        this.tempo = bpm
        tempo = bpm

        this.noteQueue = []
        this.lastNoteTimeCode = 0

        startTempo = 0
        this.beatDivisions = 1
        if (mxml.tag == 'score-partwise'):
            # Using the parts identified, look for measures belonging to that part.
            for part in mxml.iter("part"):
                # Work through each measure in the part.
                timeCode = 0.0
                partCode = part.get("id")
                for measure in part.iter("measure"):
                    # Within each measure, go through each element.
                    # Some elements are about attributes.
                    # Others are notes, rests or other timing items.
                    for musicUnit in measure:
                        if musicUnit.tag == "attributes":
                            # Additional timing info is in the time signature.
                            divisions = musicUnit.find("divisions")
                            if divisions is not None:
                                beatDivisions = int(divisions.text)

                            timeSig = musicUnit.find("time")
                            if timeSig is not None:
                                beats = timeSig.find("beats")
                                count = int(beats.text)
                                beatType = timeSig.find("beat-type")
                                countType = int(beatType.text)
                        elif musicUnit.tag == "note":
                            duration = int(musicUnit.find("duration").text)
                            timeLength = duration / beatDivisions * 60 / tempo
                            tieInfo = musicUnit.find("tie")
                            if tieInfo is not None:
                                typeOfTie = tieInfo.get("type")
                            else:
                                typeOfTie = "none"

                            # If it is not a rest, then pull out the pitch information.
                            if musicUnit.find("rest") is None and (tieInfo is None or typeOfTie == "start"):
                                chordInfo = musicUnit.find("chord")
                                if chordInfo is not None:
                                    timeCode = lastTime
                                # What note is played by pitch?
                                pitchInfo = musicUnit.find("pitch")
                                octave = pitchInfo.find("octave")
                                step = pitchInfo.find("step")
                                alter = pitchInfo.find("alter")
                                # What type of note?
                                symbol = musicUnit.find("type").text

                                # Translate to standard information
                                tone = toneLookup.get(step.text)
                                adjust = 0
                                if alter is not None:
                                    adjust = int(alter.text)
                                    tone = tone + adjust
                                if octave is None:
                                    octave = 4
                                else:
                                    octave = int(octave.text)

                                # Standardize in case sharps or flats shift to different octave
                                noteIndex = 12*octave+tone
                                octave = noteIndex // 12
                                tone = noteIndex % 12
                                # If accompanyParts is empty, all parts are included in the accompaniment.
                                if len(this.accompanyParts)==0 or partCode in this.accompanyParts:
                                    theNote = Note(tone, adjust, octave, symbol, timeCode, timeLength)
                                    this.accompaniment.append(theNote)

                                if partCode in players:
                                    adjustedTone = 12*octave + tone
                                    while adjustedTone > HIGHEST_NOTE:
                                        octave = octave - 1
                                        adjustedTone = 12*octave + tone
                                    while adjustedTone < LOWEST_NOTE:
                                        octave = octave + 1
                                        adjustedTone = 12*octave + tone
                                    theNote = Note(tone, adjust, octave, symbol, timeCode, timeLength)
                                    this.playNotes.append(theNote)

                            lastTime = timeCode
                            timeCode = timeCode + timeLength


                        # Shift time backwards to get additional notes in the measure
                        elif musicUnit.tag == "backup":
                            duration = int(musicUnit.find("duration").text)
                            # Convert to seconds
                            timeCode = timeCode - duration / beatDivisions * 60 / tempo
                            lastTime = timeCode

                        # Shift time forwards without rest to get next note in the measure
                        elif musicUnit.tag == "forward":
                            duration = int(musicUnit.find("duration").text)
                            # Convert to seconds
                            timeCode = timeCode + duration / beatDivisions * 60 / tempo
                            lastTime = timeCode

        elif (mxml.tag == 'score-timewise'):
            # This structure has multiple measures. Each measure has multiple parts.
            pass
        else:
            print("Score structure not recognized.")

        # Sort the notes into time-based ordering.
        this.playNotes.sort(key = lambda note : note.octave)
        this.playNotes.sort(key = lambda note : note.tone)
        this.playNotes.sort(key = lambda note : note.timeCode)

        this.accompaniment.sort(key = lambda note : note.octave)
        this.accompaniment.sort(key = lambda note : note.tone)
        this.accompaniment.sort(key = lambda note : note.timeCode)
        this.restartSong()

    def restartSong(this):
        global paused
        paused = False
        this.clock = pygame.time.Clock()

        this.timeCode = -timeOnScreen
        this.lastNoteTimeCode = this.timeCode
        firstNote = 0
        this.startTempo = this.tempo
        this.timeFactor = 1

    def updateScreen(this):
        # Set the screen background
        screen.fill(WHITE)

        # Draw the line where we should play.
        pygame.draw.line(screen, BLACK, [0,FLASHLINE], [WIDTH,FLASHLINE], 5)

        # Draw the title of the song
        titleText = create_text(this.songTitle, nameFonts, 36, GRAY)
        screen.blit(titleText,
                    ((WIDTH - titleText.get_width()) // 2, HEIGHT // 4))

        # Draw BPM
        bpmText = create_text(str(this.tempo) + " bpm", nameFonts, 24, GRAY)
        screen.blit(bpmText,
                    ((WIDTH - bpmText.get_width()) // 2, HEIGHT // 4 + 36))

        # Process each note that should appear on the screen.
        i = 0
        drawQueue = []
        noteQueue = set()
        
        if this.octaves=='1':
            refPos = 100
            spacing = (WIDTH-200) // 12
        else:
            refPos = WIDTH//2
            spacing = (WIDTH-200) // 24
        while i < len(this.playNotes):
            nextNote = this.playNotes[i]
            octave = nextNote.octave
            tone = nextNote.tone
            x = refPos + ((octave-4)*12 + tone)*spacing
            noteName = diatonicNames[tone] + str(octave)
            if not noteName in noteQueue:
                addNote = DrawNote(nextNote, x, STARTLINE, this.timeCode)
                drawQueue.append(addNote)
                noteQueue.add(noteName)

            if this.timeCode - 0/this.timeFactor/4 < nextNote.timeCode and nextNote.timeCode < this.timeCode + timeOnScreen/this.timeFactor:
                # Draw the note
                y = STARTLINE + int((FLASHLINE-STARTLINE)*(1 + (this.timeCode - nextNote.timeCode)*this.timeFactor/timeOnScreen))
                addNote = DrawNote(nextNote, x, y, this.timeCode)
                drawQueue.append(addNote)

            i = i+1

        for note in drawQueue:
            drawDashedHLine(screen, note.y, 10, 20)
        for drawNote in drawQueue:
            drawNote.note.draw(screen, [drawNote.x, drawNote.y], drawNote.time)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
    
    def updateNoteQueue(this):
        global debugScore

        # Find all notes that should have turned off.
        offQueue = []
        for note in this.noteQueue:
            time = note.timeCode + note.timeLength
            if time > this.lastNoteTimeCode and time <= this.timeCode:
                offQueue.append(note)

        for note in offQueue:
            pitch = 12 + 12*note.octave + note.tone
            midiDevice.note_off(pitch)
            this.noteQueue.remove(note)

        # Turn on new notes
        newNote = False
        for note in this.accompaniment:
            if note.timeCode > this.lastNoteTimeCode and note.timeCode <= this.timeCode:
                newNote = True
                if debugScore:
                    print(diatonicNames[note.tone], note.octave, sep='', end=' ')
                pitch = 12 + 12*note.octave + note.tone
                midiDevice.note_on(pitch, 100)
                this.noteQueue.append(note)
        if newNote and debugScore:
            print()
        this.lastNoteTimeCode = this.timeCode

    def doUpdate(this):
        this.updateScreen()
        this.updateNoteQueue()
        this.clock.tick(100)
        this.timeCode = this.timeCode + this.clock.get_time()/1000/this.timeFactor

    def resetNoteQueue(this, midiDevice):
        for note in this.noteQueue:
            pitch = 12 + 12*note.octave + note.tone
            midiDevice.note_off(pitch)

    def handleEvent(this, event):
        global paused

        if event.type == pygame.QUIT:  # If user clicked close
            this.done = True   # Flag that we are done so we exit this loop
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ("Pause...")
                paused = not paused
                this.resetNoteQueue(midiDevice)
                this.clock.tick()
            elif event.key == pygame.K_RETURN:
                this.resetNoteQueue(midiDevice)
                this.restartSong()
            elif event.key == pygame.K_DELETE:
                this.resetNoteQueue(midiDevice)
                this.restartSong()
            elif event.key == pygame.K_ESCAPE:
                this.resetNoteQueue(midiDevice)
                controller.active = controller.stack.pop()
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                this.tempo = this.tempo + 4
                this.timeFactor = this.startTempo / this.tempo
            elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                this.tempo = this.tempo - 4
                this.timeFactor = this.startTempo / this.tempo

class ControlManager(object):
    stack = []

diatonicNames = {0:"C", 1:"Db", 2:"D", 3:"Eb", 4:"E", 5:"F", 6:"Gb", 7:"G", 8:"Ab", 9:"A", 10:"Bb", 11:"B"}
flat = "b"
natural = ""
sharp = "#"

def getNoteName(tone, adjust):
    refTone = (tone - adjust) % 12
    name = diatonicNames[refTone]
    if adjust < 0:
        for i in range(-adjust):
            name = name + flat
    elif adjust > 0:
        for i in range(adjust):
            name = name + sharp
    return name

def make_font(fonts, size):
    available = pygame.font.get_fonts()
    # get_fonts() returns a list of lowercase spaceless font names
    choices = map(lambda x:x.lower().replace(' ', ''), fonts)
    for choice in choices:
        if choice in available:
            return pygame.font.SysFont(choice, size)
    return pygame.font.Font(None, size)

_cached_fonts = {}
def get_font(font_preferences, size):
    global _cached_fonts
    key = str(font_preferences) + '|' + str(size)
    font = _cached_fonts.get(key, None)
    if font == None:
        font = make_font(font_preferences, size)
        _cached_fonts[key] = font
    return font

_cached_text = {}
def create_text(text, fonts, size, color):
    global _cached_text
    key = '|'.join(map(str, (fonts, size, color, text)))
    image = _cached_text.get(key, None)
    if image == None:
        font = get_font(fonts, size)
        image = font.render(text, True, color)
        _cached_text[key] = image
    return image

nameFonts = ["Arial Unicode MS", "Helvetica"]

class DrawNote():
    def __init__(self, note, x, y, timeCode):
        self.note = note
        self.x = x
        self.y = y
        self.time = timeCode

class Note():
    def __init__(self, tone, adjust, octave, symbol, timeCode, timeLength):
        self.tone = tone
        self.adjust = adjust
        self.octave = octave
        self.symbol = symbol
        self.timeCode = timeCode
        self.timeLength = timeLength

    def draw(self, screen, pos, curTime):
        global nameFonts

        color = color_list[self.tone]
        noteName = getNoteName(self.tone, self.adjust)
        radius = NOTESIZE
        noteRect = pygame.draw.circle(screen, color, pos, radius)
        noteRect = pygame.draw.circle(screen, BLACK, pos, radius, 1)
        noteText = create_text(noteName, nameFonts, 18, WHITE)
        noteTextShadow = create_text(noteName, nameFonts, 18, BLACK)
        screen.blit(noteTextShadow,
            (pos[0] - noteText.get_width() // 2 - 1, pos[1] - noteText.get_height() // 2 - 1))
        screen.blit(noteTextShadow,
            (pos[0] - noteText.get_width() // 2 + 1, pos[1] - noteText.get_height() // 2 - 1))
        screen.blit(noteTextShadow,
            (pos[0] - noteText.get_width() // 2 - 1, pos[1] - noteText.get_height() // 2))
        screen.blit(noteTextShadow,
            (pos[0] - noteText.get_width() // 2 + 1, pos[1] - noteText.get_height() // 2))
        screen.blit(noteTextShadow,
            (pos[0] - noteText.get_width() // 2 - 1, pos[1] - noteText.get_height() // 2 + 1))
        screen.blit(noteTextShadow,
            (pos[0] - noteText.get_width() // 2 + 1, pos[1] - noteText.get_height() // 2 + 1))
        screen.blit(noteText,
            (pos[0] - noteText.get_width() // 2, pos[1] - noteText.get_height() // 2))


# ----------
#    This function imports the musicxml data from the song stored in filePath.
#    It then pulls out the notes associated with the given parts for presentation
#    in a music flow.
#
#    Returns a song object.
# ----------

def drawDashedHLine(screen, y, onDash, offDash):
    x=0
    while x < WIDTH:
        pygame.draw.line(screen, BLACK, [x,y], [x+onDash,y], 1)
        x = x + onDash + offDash


# Initialize the game engine
pygame.init()
musicFont = pygame.font.SysFont("comicsansms", 18)

# Set the height and width of the screen
screen = pygame.display.set_mode((1400,840))
print(screen)
pygame.display.set_caption("Falling Music")
WIDTH = screen.get_width()
HEIGHT = screen.get_height()
STARTLINE = 60
FLASHLINE = int(0.8 * HEIGHT)
if args.octaves=='1':
    NOTESIZE = 36
else:
    NOTESIZE = 18

# How many seconds worth of advance notice?
timeOnScreen = 4
paused = False

# Find a MIDI synthesizer
pygame.midi.init()

# Find the synthesizer
midiDeviceNumber = pygame.midi.get_default_output_id()
midiDevice = pygame.midi.Output(midiDeviceNumber)

# Create an empty array
numcolors = len(color_list)
color_width = WIDTH // numcolors + 1

workNote = QuarterNote(3, 4, 4, True)
controller = ControlManager()
controller.active = SongSelector()

print(args.folder)
controller.active.loadSongList(args.folder)

while (not controller.active.done):
    # Deal with event management
    for event in pygame.event.get():   # User did something
        controller.active.handleEvent(event)

    if paused:
        pygame.time.wait(200)
        continue

    # Update processes and graphics
    controller.active.doUpdate()

# Be IDLE friendly. If you forget this line, the program will 'hang' on exit.
print("Cleaning Up.")
pygame.quit()
sys.exit()
