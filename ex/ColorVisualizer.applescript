-- Color Visualizer with Visual Spectrum Display
-- Supports: HEX, RGB, CMYK, HSL, HSB color formats
-- Uses Python + Pillow to generate visual color spectrum

use AppleScript version "2.4"
use scripting additions

on run
	set dialogText to "Enter a color value:" & return & return
	set dialogText to dialogText & "Supported formats:" & return
	set dialogText to dialogText & "- HEX: #ffb6c1 or ffb6c1" & return
	set dialogText to dialogText & "- RGB: rgb(255, 182, 193) or 255,182,193" & return
	set dialogText to dialogText & "- CMYK: cmyk(0, 29, 24, 0)" & return
	set dialogText to dialogText & "- HSL: hsl(351, 100, 86)" & return
	set dialogText to dialogText & "- HSB/HSV: hsb(351, 29, 100)"
	
	set colorInput to text returned of (display dialog dialogText default answer "#ffb6c1" buttons {"Cancel", "Visualize"} default button "Visualize")
	
	set rgbColor to my parseColorInput(colorInput)
	
	if rgbColor is missing value then
		display dialog "Could not parse color: " & colorInput buttons {"OK"} default button "OK" with icon stop
		return
	end if
	
	set rVal to item 1 of rgbColor
	set gVal to item 2 of rgbColor
	set bVal to item 3 of rgbColor
	
	-- Convert to hex for Python script
	set hexColor to my rgbToHex(rVal, gVal, bVal)
	
	-- Generate and display the spectrum image
	my showColorSpectrum(hexColor, colorInput)
end run

on showColorSpectrum(hexColor, originalInput)
	-- Find Python3 path
	set pythonPath to "/opt/homebrew/bin/python3"
	try
		do shell script "test -f " & pythonPath
	on error
		-- Try other common locations
		try
			set pythonPath to "/usr/local/bin/python3"
			do shell script "test -f " & pythonPath
		on error
			try
				set pythonPath to "/usr/bin/python3"
				do shell script "test -f " & pythonPath
			on error
				display dialog "Python 3 not found. Please install Python 3." buttons {"OK"} default button "OK" with icon stop
				return
			end try
		end try
	end try
	
	-- Check if Pillow is available
	try
		do shell script pythonPath & " -c 'import PIL' 2>&1"
	on error
		display dialog "Pillow library is required." & return & return & "Install with: " & pythonPath & " -m pip install pillow" buttons {"OK"} default button "OK" with icon caution with title "Missing Dependencies"
		return
	end try
	
	-- Find the Python script - try multiple locations
	set pythonScript to ""
	set foundScript to false
	
	-- Location 1: Check in app bundle Resources
	try
		set appPath to POSIX path of (path to me)
		-- Extract .app path if we're inside the bundle
		if appPath contains ".app/" then
			set AppleScript's text item delimiters to ".app/"
			set appBundlePath to (text item 1 of appPath) & ".app"
			set AppleScript's text item delimiters to ""
			set pythonScript to appBundlePath & "/Contents/Resources/generate_color_image.py"
			
			do shell script "test -f " & quoted form of pythonScript
			set foundScript to true
		end if
	end try
	
	-- Location 2: Check in same directory as script
	if not foundScript then
		try
			set appPath to POSIX path of (path to me)
			set scriptDir to do shell script "dirname " & quoted form of appPath
			set pythonScript to scriptDir & "/generate_color_image.py"
			
			do shell script "test -f " & quoted form of pythonScript
			set foundScript to true
		end try
	end if
	
	-- Location 3: Use hardcoded fallback path
	if not foundScript then
		set pythonScript to "/Users/yoojinseon/Develop/ScriptEditor/color-visualizer/generate_color_image.py"
		try
			do shell script "test -f " & quoted form of pythonScript
			set foundScript to true
		on error
			display dialog "Cannot find generate_color_image.py script!" buttons {"OK"} default button "OK" with icon stop
			return
		end try
	end if
	
	-- Output PNG path (use /tmp for better permissions)
	set outputPNGPosix to "/tmp/color_spectrum.png"
	
	-- Generate color spectrum image
	try
		do shell script pythonPath & " " & quoted form of pythonScript & " " & quoted form of hexColor & " " & quoted form of outputPNGPosix
	on error errMsg
		display dialog "Error generating spectrum: " & errMsg buttons {"OK"} default button "OK" with icon stop
		return
	end try
	
	-- Open PNG in Preview.app
	do shell script "open -a Preview " & quoted form of outputPNGPosix
end showColorSpectrum

on parseColorInput(inputText)
	set inputText to my trimText(inputText)
	set inputLower to my lowercaseText(inputText)
	
	if inputText starts with "#" then
		return my parseHex(inputText)
	end if
	
	if (length of inputText is 6) and (my isHexString(inputText)) then
		return my parseHex(inputText)
	end if
	
	if (length of inputText is 3) and (my isHexString(inputText)) then
		return my parseHex(inputText)
	end if
	
	if inputLower starts with "rgb" then
		return my parseRGB(inputText)
	end if
	
	if inputLower starts with "cmyk" then
		return my parseCMYK(inputText)
	end if
	
	if inputLower starts with "hsl" then
		return my parseHSL(inputText)
	end if
	
	if inputLower starts with "hsb" or inputLower starts with "hsv" then
		return my parseHSB(inputText)
	end if
	
	if inputText contains "," then
		return my parseRGB(inputText)
	end if
	
	return missing value
end parseColorInput

on parseHex(hexString)
	if hexString starts with "#" then
		set hexString to text 2 thru -1 of hexString
	end if
	
	if length of hexString is 3 then
		set c1 to character 1 of hexString
		set c2 to character 2 of hexString
		set c3 to character 3 of hexString
		set hexString to c1 & c1 & c2 & c2 & c3 & c3
	end if
	
	if length of hexString is not 6 then
		return missing value
	end if
	
	try
		set rHex to text 1 thru 2 of hexString
		set gHex to text 3 thru 4 of hexString
		set bHex to text 5 thru 6 of hexString
		
		set rVal to my hexToDecimal(rHex)
		set gVal to my hexToDecimal(gHex)
		set bVal to my hexToDecimal(bHex)
		
		return {rVal, gVal, bVal}
	on error
		return missing value
	end try
end parseHex

on parseRGB(rgbString)
	try
		set nums to my extractNumbers(rgbString)
		if (count of nums) < 3 then return missing value
		
		set rVal to item 1 of nums
		set gVal to item 2 of nums
		set bVal to item 3 of nums
		
		if rVal > 255 then set rVal to 255
		if gVal > 255 then set gVal to 255
		if bVal > 255 then set bVal to 255
		if rVal < 0 then set rVal to 0
		if gVal < 0 then set gVal to 0
		if bVal < 0 then set bVal to 0
		
		return {rVal, gVal, bVal}
	on error
		return missing value
	end try
end parseRGB

on parseCMYK(cmykString)
	try
		set nums to my extractNumbers(cmykString)
		if (count of nums) < 4 then return missing value
		
		set c to (item 1 of nums) / 100
		set m to (item 2 of nums) / 100
		set yy to (item 3 of nums) / 100
		set k to (item 4 of nums) / 100
		
		set rVal to round (255 * (1 - c) * (1 - k))
		set gVal to round (255 * (1 - m) * (1 - k))
		set bVal to round (255 * (1 - yy) * (1 - k))
		
		return {rVal, gVal, bVal}
	on error
		return missing value
	end try
end parseCMYK

on parseHSL(hslString)
	try
		set nums to my extractNumbers(hslString)
		if (count of nums) < 3 then return missing value
		
		set h to (item 1 of nums) / 360
		set s to (item 2 of nums) / 100
		set lum to (item 3 of nums) / 100
		
		return my hslToRGB(h, s, lum)
	on error
		return missing value
	end try
end parseHSL

on parseHSB(hsbString)
	try
		set nums to my extractNumbers(hsbString)
		if (count of nums) < 3 then return missing value
		
		set h to (item 1 of nums) / 360
		set s to (item 2 of nums) / 100
		set v to (item 3 of nums) / 100
		
		return my hsbToRGB(h, s, v)
	on error
		return missing value
	end try
end parseHSB

on hslToRGB(h, s, lum)
	if s = 0 then
		set grayVal to round (lum * 255)
		return {grayVal, grayVal, grayVal}
	end if
	
	set q to 0
	if lum < 0.5 then
		set q to lum * (1 + s)
	else
		set q to lum + s - lum * s
	end if
	set p to 2 * lum - q
	
	set rVal to round ((my calcHue(p, q, h + 0.333333)) * 255)
	set gVal to round ((my calcHue(p, q, h)) * 255)
	set bVal to round ((my calcHue(p, q, h - 0.333333)) * 255)
	
	return {rVal, gVal, bVal}
end hslToRGB

on calcHue(p, q, t)
	if t < 0 then set t to t + 1
	if t > 1 then set t to t - 1
	if t < 0.166667 then return p + (q - p) * 6 * t
	if t < 0.5 then return q
	if t < 0.666667 then return p + (q - p) * (0.666667 - t) * 6
	return p
end calcHue

on hsbToRGB(h, s, v)
	if s = 0 then
		set grayVal to round (v * 255)
		return {grayVal, grayVal, grayVal}
	end if
	
	set h to h * 6
	set i to h div 1
	set f to h - i
	set pVal to v * (1 - s)
	set qVal to v * (1 - s * f)
	set tVal to v * (1 - s * (1 - f))
	
	if i = 0 or i = 6 then
		set rgbList to {v, tVal, pVal}
	else if i = 1 then
		set rgbList to {qVal, v, pVal}
	else if i = 2 then
		set rgbList to {pVal, v, tVal}
	else if i = 3 then
		set rgbList to {pVal, qVal, v}
	else if i = 4 then
		set rgbList to {tVal, pVal, v}
	else
		set rgbList to {v, pVal, qVal}
	end if
	
	set rVal to round ((item 1 of rgbList) * 255)
	set gVal to round ((item 2 of rgbList) * 255)
	set bVal to round ((item 3 of rgbList) * 255)
	
	return {rVal, gVal, bVal}
end hsbToRGB

on rgbToHex(rVal, gVal, bVal)
	set rHex to my decimalToHex(rVal)
	set gHex to my decimalToHex(gVal)
	set bHex to my decimalToHex(bVal)
	return "#" & rHex & gHex & bHex
end rgbToHex

on decimalToHex(decVal)
	if decVal < 0 then set decVal to 0
	if decVal > 255 then set decVal to 255
	set decVal to decVal as integer
	set hexChars to "0123456789ABCDEF"
	set h1 to character ((decVal div 16) + 1) of hexChars
	set h2 to character ((decVal mod 16) + 1) of hexChars
	return h1 & h2
end decimalToHex

on hexToDecimal(hexStr)
	set hexStr to my uppercaseText(hexStr)
	set hexChars to "0123456789ABCDEF"
	set decResult to 0
	repeat with i from 1 to length of hexStr
		set c to character i of hexStr
		set pos to offset of c in hexChars
		if pos = 0 then return 0
		set decResult to decResult * 16 + (pos - 1)
	end repeat
	return decResult
end hexToDecimal

on uppercaseText(str)
	set lowers to "abcdef"
	set uppers to "ABCDEF"
	set outStr to ""
	repeat with c in str
		set c to c as text
		set pos to offset of c in lowers
		if pos > 0 then
			set outStr to outStr & character pos of uppers
		else
			set outStr to outStr & c
		end if
	end repeat
	return outStr
end uppercaseText

on lowercaseText(str)
	set uppers to "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	set lowers to "abcdefghijklmnopqrstuvwxyz"
	set outStr to ""
	repeat with c in str
		set c to c as text
		set pos to offset of c in uppers
		if pos > 0 then
			set outStr to outStr & character pos of lowers
		else
			set outStr to outStr & c
		end if
	end repeat
	return outStr
end lowercaseText

on trimText(str)
	set str to str as text
	if str is "" then return ""
	repeat while str starts with " "
		if length of str > 1 then
			set str to text 2 thru -1 of str
		else
			return ""
		end if
	end repeat
	repeat while str ends with " "
		if length of str > 1 then
			set str to text 1 thru -2 of str
		else
			return ""
		end if
	end repeat
	return str
end trimText

on isHexString(str)
	set hexChars to "0123456789ABCDEFabcdef"
	repeat with c in str
		if offset of (c as text) in hexChars is 0 then
			return false
		end if
	end repeat
	return true
end isHexString

on extractNumbers(str)
	set nums to {}
	set currentNum to ""
	
	repeat with i from 1 to length of str
		set c to character i of str
		if c is in "0123456789" then
			set currentNum to currentNum & c
		else if c is "." then
			set currentNum to currentNum & c
		else
			if currentNum is not "" then
				try
					set end of nums to (currentNum as number)
				end try
				set currentNum to ""
			end if
		end if
	end repeat
	
	if currentNum is not "" then
		try
			set end of nums to (currentNum as number)
		end try
	end if
	
	return nums
end extractNumbers
