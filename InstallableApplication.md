Instructions for using the program as an installable application

# Introduction #

If you're not interested in programmatic access to the tags inside an `.aa` file, and just want a program that will organize your audiobooks for you, then you should download the setup program from the Downloads tab.

# Installing the Program #

Run `setup-1.x.x.exe`. If you have installed any other program you will find this installer straightforward to use.

# Running the Program #

Organizaa is a _command-line program_. It won't work if you just double-click on it, because you have to tell it what folder you want organized.

## Quick Instructions ##

If you are comfortable using command-line programs this will be all you need:

Invoke as in this example: `organizaa "F:\My Audio Books"`

## Step-by-Step Instructions ##

1. Open a Windows console as follows: select `Start | Run...` and when prompted `Open:` type `cmd` and press OK.

2. You will now have a Windows console session (also inaccurately called a "DOS box").

3. Type `cd` at the prompt, and then a space, but don't press Enter.

4. Find the folder where you installed Organizaa. Then drag the folder name from Explorer to the Windows console session. Windows will type the complete folder name for you.

5. Your command line should look like this:
```
cd "C:\Program Files\Rocket Cottage\Organizaa"
```
Press Enter.

6. Now type `organizaa` at the prompt, and then a space, but don't press Enter.

7. Find the audiobook folder that you want to reorganize and drag the folder name from Explorer to the Windows console session. Windows will type the complete folder name for you.

8. Your command line should look like this:
```
organizaa "C:\My Audio Books"
```
Press Enter.

After a few moments the program will report the number of files it has moved. You're done.

## Creating a Shortcut ##

If you are going to want to do this regularly, create a shortcut to run the progam.

1. In Explorer, open the folder where you installed Organizaa and right-click-drag organizaa.exe to the desktop (or somewhere else you find convenient).

2. When you drop the file on the desktop, take the option _Create shortcut here_. It will be called _Shortcut to organizaa.exe_.

3. Right-click the shortcut and select _Properties_. On the Shortcut tab, edit the Target field by adding the name of your audiobook folder. Like this:

> - Before: `"C:\Program Files\Rocket Cottage\Organizaa\organizaa.exe"`

> - After:  `"C:\Program Files\Rocket Cottage\Organizaa\organizaa.exe" "F:\My Audiobooks"`

4. If you want, on the General tab, change the name from `Shortcut to...` to something more convenient.

5. Press OK. Now double-click the shortcut to run the program.