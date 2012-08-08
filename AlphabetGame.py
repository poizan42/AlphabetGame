# -*- coding: utf8 -*-
# AlphabetGame v. 0.3
#
# Copyright (c) Kasper F. Brandt 2009,2012
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the owner nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import time

class _Getch:
    """
    Gets a single character from standard input.  Does not echo to
    the screen.
    """
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            try:
                self.impl = _GetchMacCarbon()
            except(AttributeError, ImportError):
                self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys, termios # import termios now or else you'll get the Unix version on the Mac

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


class _GetchMacCarbon:
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned.  The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """
    def __init__(self):
        import Carbon
        Carbon.Evt #see if it has this (in Unix, it doesn't)

    def __call__(self):
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask
            return ''
        else:
            #
            # The event contains the following info:
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned
            #
            (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)


getch = _Getch()

locales = {}
daloc = {
	'intro0': "Skriv alfabetet fra a-z s\x86 hurtigt som muligt",
	'intro1': "Start p\x86 a (- for at slutte):",
	'lost': "Du har tabt spillet!",
	'won': "Du vandt spillet!",
	'stattime': "Tid: %.3f s",
	'statkeystrokes': "Anslag/minut: %.1f\n"
}
locales['da'] = daloc
enloc = {
	'intro0': "Type the alphabet from a-z as fast as possible",
	'intro1': "Start with a (- to quit):",
	'lost': "You have lost the game!",
	'won': "You have won the game!",
	'stattime': "Time: %.3f s",
	'statkeystrokes': "Keystrokes/minute: %.1f\n"
}
locales['en'] = enloc

locale = locales['en']

while True:
    fail = False
    print locale['intro0']
    print locale['intro1']
    pos = 0
    while pos < 26:
        c = getch()
        if c == '-':
            exit(0)
        if pos == 0 and c != 'a':
            pos = 0
            continue
        if pos == 0:
            starttime = time.time()
        sys.stdout.write(c)
        if (c != chr(ord('a')+pos)):
            print "\n\n" + locale['lost']
            timeSpan = time.time()-starttime
            print locale['stattime'] % timeSpan
            print locale['statkeystrokes'] % (60*pos/timeSpan)
            fail = True
            break
        pos += 1
    if fail:
        continue

    print "\n" + locale['won']
    timeSpan = time.time()-starttime
    print locale['stattime'] % timeSpan
    print locale['statkeystrokes'] % (60*26/timeSpan)
