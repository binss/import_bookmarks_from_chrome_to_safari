set SecondsDelay to 0.1

tell application "Safari" to activate
delay SecondsDelay
tell application "Safari" to close windows

tell application "System Events" to tell process "Safari"
	tell menu item "Import From" of menu "File" of menu bar item "File" of menu bar 1
		tell menu "Import From"
			click menu item "Google Chrome…"
		end tell
	end tell
	tell window "Import from Google Chrome"
		click button "Import"
	end tell
end tell