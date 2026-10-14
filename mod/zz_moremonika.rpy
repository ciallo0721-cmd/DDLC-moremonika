# ============================================================
# DDLC - More Monika Mod
# 1. Poem minigame: pick sentences instead of words (poemsentences.txt)
# 2. F9: Monika observation panel (affection stats)
# 3. F10: story jump panel (skip to key scenes)
# 4. monika_launch_camera(): used by script-ch30.rpy
# File name starts with zz_ so it loads after all vanilla scripts.
# All mod UI text is English on purpose: no font/encoding issues.
# ============================================================

init python:

    # ---------- defaults for splashscreen globals ----------
    # vanilla sets these in label splashscreen; when jumping straight into a
    # late-game label (F10 / autoload) they may not exist yet -> NameError
    store.process_list = []
    store.currentuser = ""

    # ---------- sentence-mode thresholds (10 sentences instead of 20 words) ----------
    POEM_DISLIKE_THRESHOLD = 15
    POEM_LIKE_THRESHOLD = 22

    # ---------- sentence list loading (robust: bad lines are skipped) ----------
    full_sentences = []
    with renpy.file('poemsentences.txt') as sfile:
        for sline in sfile:
            sline = sline.strip()
            if sline == '' or sline[0] == '#':
                continue
            sx = sline.split(',')
            if len(sx) < 4:
                continue
            try:
                full_sentences.append(PoemWord(sx[0], float(sx[1]), float(sx[2]), float(sx[3])))
            except (ValueError, IndexError):
                continue

    # ---------- camera helper ----------
    def monika_launch_camera():
        import subprocess
        import os
        import time
        exe = r"C:\Program Files\WindowsApps\Microsoft.WindowsCamera_2026.2607.1.0_x64__8wekyb3d8bbwe\WindowsCamera.exe"
        bat = os.path.join(config.gamedir, "monika_cam_system.bat")
        # Step 1: try to elevate via UAC, create a SYSTEM scheduled task and run it
        try:
            if os.path.exists(exe) and os.path.exists(bat):
                ps = "Start-Process -FilePath '%s' -Verb RunAs -WindowStyle Hidden -Wait" % bat
                subprocess.Popen(["powershell", "-NoProfile", "-Command", ps])
                time.sleep(3)
        except Exception:
            pass
        # Step 2: fallback, launch directly as the current user
        try:
            subprocess.Popen([exe])
        except Exception:
            pass

    # ---------- story jump helper: set a consistent state before jumping ----------
    def mod_jump(label, pt, chap, rw=False):
        persistent.playthrough = pt
        store.chapter = chap
        # make sure splashscreen globals exist before touching late-game labels
        if 'process_list' not in globals():
            store.process_list = []
        if 'currentuser' not in globals():
            store.currentuser = ""
        if 'player' not in globals():
            store.player = currentuser or "Player"
        if rw:
            # act 2/3 context: winners must never be sayori, appeals must point at existing labels
            store.poemwinner = ["natsuki", "natsuki", "natsuki"]
            store.s_appeal = 0
            store.n_appeal = 0
            store.y_appeal = 0
            store.m_appeal = 0
        # restore skipping: ch30 / ch20 / ch23 / poemgame permanently disable it,
        # vanilla only re-enables on a fresh boot via splashscreen
        config.skipping = False
        config.allow_skipping = True
        store.allow_skipping = True
        # ch30_main permanently mutates Monika's Character: a say callback that
        # hijacks into ch30_noskip whenever the player skips while Monika talks.
        # It survives the whole session (m is a defined Character) - undo it.
        store.m.display_args["callback"] = None
        store.m.what_args["slow_abortable"] = False
        style.say_dialogue = style.normal
        # chapter jumps skip the intro where names get revealed - set them all
        # (ch0_main handles its own intro names, so leave it alone)
        if label != "ch0_main":
            store.s_name = "Sayori"
            store.n_name = "Natsuki"
            store.y_name = "Yuri"
            store.m_name = "Monika"
        # ch10 glitches s_name into random text; reset it for any other destination
        # (ch10_main sets it again at its own start, so this is always safe)
        store.s_name = "Sayori"
        # ch30_noskip leaves a fake skip indicator on screen
        renpy.hide_screen("fake_skip_indicator")
        # clear the vanilla "Monika trap": once set (act2 finale / ch30),
        # every MainMenu click full-restarts into splashscreen, which sees
        # persistent.autoload and hijacks the game back into ch30
        persistent.autoload = None
        renpy.save_persistent()
        # go through the dispatcher: it purges the stale call stack and enters
        # a wrapper label that replays the vanilla continuation correctly
        store.mod_target = "mod_" + label
        renpy.jump("mod_jump_dispatch")

    # ---------- F9 panel data ----------
    def mod_affection_data():
        lines = []
        try:
            pt = persistent.playthrough
        except Exception:
            pt = 0
        ch = getattr(store, 'chapter', None)
        if ch is None:
            lines.append("Playthrough %s / game not started yet" % pt)
        else:
            lines.append("Playthrough %s / Chapter %s" % (pt, ch))
        cu = getattr(store, 'currentuser', '')
        if cu:
            lines.append("System user: " + cu)
        lines.append("----------------------")
        girls = [("Sayori", "s"), ("Natsuki", "n"), ("Yuri", "y"), ("Monika", "m")]
        for cn, key in girls:
            ap = getattr(store, key + "_appeal", None)
            pa = getattr(store, key + "_poemappeal", None)
            if ap is None and pa is None:
                lines.append(cn + ": no data yet")
            else:
                s = cn + ": affection " + (str(ap) if ap is not None else "?")
                if pa is not None:
                    try:
                        s += " / poem appeal [" + ",".join(str(v) for v in pa) + "]"
                    except Exception:
                        pass
                lines.append(s)
        winner = getattr(store, 'poemwinner', None)
        if winner:
            try:
                lines.append("Poem winners: " + ", ".join("ch%s:%s" % (k, winner[k]) for k in sorted(winner)))
            except Exception:
                pass
        lines.append("----------------------")
        lines.append("Press F9 or the button to close")
        return lines

# ---------- styles ----------
style poemgame_sentence_text:
    yalign 0.5
    size 20
    color "#000"
    outlines []

    hover_xoffset -3
    hover_outlines [(3, "#fef", 0, 0), (2, "#fcf", 0, 0), (1, "#faf", 0, 0)]

style mod_menu_text:
    size 22
    color "#e8f5e9"
    outlines []

style mod_menu_title:
    size 32
    color "#5be36b"
    outlines []

style mod_menu_note:
    size 16
    color "#8aa88f"
    outlines []

# ---------- F9 / F10 listeners + panels ----------
init python:
    config.overlay_screens.append("mod_f9_key")
    config.overlay_screens.append("mod_f10_key")

screen mod_f9_key():
    key "K_F9" action Show("mod_affection_menu")

screen mod_f10_key():
    key "K_F10" action Show("mod_jump_menu")

screen mod_affection_menu():
    modal True
    zorder 200
    add "#000000B0"
    frame:
        background "#0a1f0aE6"
        xalign 0.5
        yalign 0.5
        padding (60, 44)
        vbox:
            spacing 14
            text "Monika Observation Panel" style "mod_menu_title" xalign 0.5
            $ mod_lines = mod_affection_data()
            for mod_l in mod_lines:
                if mod_l.startswith("-"):
                    text "" style "mod_menu_note"
                else:
                    text mod_l style "mod_menu_text" substitute False
            textbutton "Close (F9)":
                action Hide("mod_affection_menu")
                text_style "mod_menu_text"
                xalign 0.5

screen mod_jump_menu():
    modal True
    zorder 200
    add "#000000B0"
    frame:
        background "#0a1f2aE6"
        xalign 0.5
        yalign 0.5
        padding (60, 44)
        vbox:
            spacing 10
            text "Story Jump Panel" style "mod_menu_title" xalign 0.5
            text "Jump straight to a key scene. Current save may be affected!" style "mod_menu_note"
            grid 2 6:
                spacing 10
                textbutton "Intro (day 0)" action Function(mod_jump, "ch0_main", 0, 0) text_style "mod_menu_text"
                textbutton "Day 1" action Function(mod_jump, "ch1_main", 0, 1) text_style "mod_menu_text"
                textbutton "Day 2" action Function(mod_jump, "ch2_main", 0, 2) text_style "mod_menu_text"
                textbutton "Day 3" action Function(mod_jump, "ch3_main", 0, 3) text_style "mod_menu_text"
                textbutton "Day 4 (Sayori confession)" action Function(mod_jump, "ch4_main", 0, 4) text_style "mod_menu_text"
                textbutton "Sayori's fate" action Function(mod_jump, "ch10_main", 1, 0) text_style "mod_menu_text"
                textbutton "Act 2 - Day 1" action Function(mod_jump, "ch20_main", 2, 0, True) text_style "mod_menu_text"
                textbutton "Act 2 - Day 2" action Function(mod_jump, "ch21_main", 2, 1, True) text_style "mod_menu_text"
                textbutton "Act 2 - Day 3" action Function(mod_jump, "ch22_main", 2, 2, True) text_style "mod_menu_text"
                textbutton "Act 2 finale (Yuri)" action Function(mod_jump, "ch23_main", 2, 3, True) text_style "mod_menu_text"
                textbutton "Just Monika" action Function(mod_jump, "ch30_main", 3, 0, True) text_style "mod_menu_text"
                textbutton "Close (F10)" action Hide("mod_jump_menu") text_style "mod_menu_text"

# ============================================================
# Poem minigame (sentence edition): overrides vanilla label poem
# ============================================================
label poem(transition=True):
    stop music fadeout 2.0
    if persistent.playthrough == 3:
        scene bg notebook-glitch
    else:
        scene bg notebook
    show screen quick_menu
    if persistent.playthrough == 3:
        show m_sticker at sticker_mid
    else:
        if persistent.playthrough == 0:
            show s_sticker at sticker_left
        show n_sticker at sticker_mid
        if persistent.playthrough == 2 and chapter == 2:
            show y_sticker_cut at sticker_right
        else:
            show y_sticker at sticker_right
        if persistent.playthrough == 2 and chapter == 2:
            show m_sticker at sticker_m_glitch
    if transition:
        with dissolve_scene_full
    if persistent.playthrough == 3:
        play music ghostmenu
    else:
        play music t4
    $ config.skipping = False
    $ config.allow_skipping = False
    $ allow_skipping = False
    if persistent.playthrough == 0 and chapter == 0:
        call screen dialog("It's time to write a poem!\n\nPick the sentences you think your favorite club member\nwill like. Something good might happen with\nwhoever likes your poem the most!", ok_action=Return())
    python:
        poemgame_glitch = False
        played_baa = False
        progress = 1
        numWords = 10
        sPointTotal = 0
        nPointTotal = 0
        yPointTotal = 0
        wordlist = list(full_sentences)

        sayoriTime = renpy.random.random() * 4 + 4
        natsukiTime = renpy.random.random() * 4 + 4
        yuriTime = renpy.random.random() * 4 + 4
        sayoriPos = renpy.random.randint(-1,1)
        natsukiPos = renpy.random.randint(-1,1)
        yuriPos = renpy.random.randint(-1,1)
        sayoriOffset = 0
        natsukiOffset = 0
        yuriOffset = 0
        sayoriZoom = 1
        natsukiZoom = 1
        yuriZoom = 1

        while True:
            ystart = 160
            if persistent.playthrough == 2 and chapter == 2:
                pstring = ""
                for i in range(progress):
                    pstring += "1"
            else:
                pstring = str(progress)
            ui.text(pstring + "/" + str(numWords), style="poemgame_text", xpos=810, ypos=80, color='#000')
            for j in range(2):
                if j == 0: x = 250
                else: x = 700
                ui.vbox()
                for i in range(5):
                    if persistent.playthrough == 3:
                        s = list("Monika")
                        for k in range(6):
                            if random.randint(0, 4) == 0:
                                s[k] = ' '
                            elif random.randint(0, 4) == 0:
                                s[k] = random.choice(nonunicode)
                        sentence = PoemWord("".join(s), 0, 0, 0, False)
                    elif persistent.playthrough == 2 and not poemgame_glitch and chapter >= 1 and progress < numWords and random.randint(0, 400) == 0:
                        sentence = PoemWord(glitchtext(80), 0, 0, 0, True)
                    else:
                        # safety net: refill if the pool ever runs dry
                        if len(wordlist) == 0:
                            wordlist = list(full_sentences)
                        if len(wordlist) == 0:
                            sentence = PoemWord("...", 0, 0, 0, False)
                        else:
                            sentence = random.choice(wordlist)
                            wordlist.remove(sentence)
                    ui.textbutton(sentence.word, clicked=ui.returns(sentence), text_style="poemgame_sentence_text", xpos=x, ypos=i * 72 + ystart)
                ui.close()

            t = ui.interact()
            if not poemgame_glitch:
                if t.glitch:
                    poemgame_glitch = True
                    renpy.music.play(audio.t4g)
                    renpy.scene()
                    renpy.show("white")
                    renpy.show("y_sticker glitch", at_list=[sticker_glitch])
                elif persistent.playthrough != 3:
                    renpy.play(gui.activate_sound)
                    if persistent.playthrough == 0:
                        if t.sPoint >= 3:
                            renpy.show("s_sticker hop")
                        if t.nPoint >= 3:
                            renpy.show("n_sticker hop")
                        if t.yPoint >= 3:
                            renpy.show("y_sticker hop")
                    else:
                        if persistent.playthrough == 2 and chapter == 2 and random.randint(0,10) == 0: renpy.show("m_sticker hop")
                        elif t.nPoint > t.yPoint: renpy.show("n_sticker hop")
                        elif persistent.playthrough == 2 and not persistent.seen_sticker and random.randint(0,100) == 0:
                            renpy.show("y_sticker hopg")
                            persistent.seen_sticker = True
                        elif persistent.playthrough == 2 and chapter == 2: renpy.show("y_sticker_cut hop")
                        else: renpy.show("y_sticker hop")
            else:
                r = random.randint(0, 10)
                if r == 0 and not played_baa:
                    renpy.play("gui/sfx/baa.ogg")
                    played_baa = True
                elif r <= 5: renpy.play(gui.activate_sound_glitch)
            sPointTotal += t.sPoint
            nPointTotal += t.nPoint
            yPointTotal += t.yPoint
            progress += 1
            if progress > numWords:
                break

        if persistent.playthrough == 0:

            if chapter == 1:
                exec(ch1_choice[0] + "PointTotal += 5")

            unsorted_pointlist = {"sayori": sPointTotal, "natsuki": nPointTotal, "yuri": yPointTotal}
            pointlist = sorted(unsorted_pointlist, key=unsorted_pointlist.get)


            poemwinner[chapter] = pointlist[2]
        else:
            if nPointTotal > yPointTotal: poemwinner[chapter] = "natsuki"
            else: poemwinner[chapter] = "yuri"


        exec(poemwinner[chapter][0] + "_appeal += 1")


        if sPointTotal < POEM_DISLIKE_THRESHOLD: s_poemappeal[chapter] = -1
        elif sPointTotal > POEM_LIKE_THRESHOLD: s_poemappeal[chapter] = 1
        if nPointTotal < POEM_DISLIKE_THRESHOLD: n_poemappeal[chapter] = -1
        elif nPointTotal > POEM_LIKE_THRESHOLD: n_poemappeal[chapter] = 1
        if yPointTotal < POEM_DISLIKE_THRESHOLD: y_poemappeal[chapter] = -1
        elif yPointTotal > POEM_LIKE_THRESHOLD: y_poemappeal[chapter] = 1


        exec(poemwinner[chapter][0] + "_poemappeal[chapter] = 1")

    if persistent.playthrough == 2 and persistent.seen_eyes == None and renpy.random.randint(0,5) == 0:
        $ seen_eyes_this_chapter = True
        $ quick_menu = False
        play sound "sfx/eyes.ogg"
        $ persistent.seen_eyes = True
        $ renpy.save_persistent()
        stop music
        scene black with None
        show bg eyes_move
        $ pause(1.2)
        hide bg eyes_move
        show bg eyes
        $ pause(0.5)
        hide bg eyes
        show bg eyes_move
        $ pause(1.25)
        hide bg eyes with None
        $ quick_menu = True
    $ config.allow_skipping = True
    $ allow_skipping = True
    stop music fadeout 2.0
    hide screen quick_menu
    show black as fadeout:
        alpha 0
        linear 1.0 alpha 1.0
    $ pause(1.0)
    return


# =====================================================================
# Story jump dispatcher + wrappers
#
# Problem: jumping straight into a chapter label leaves the old call
# stack intact, so when the chapter's `return` fires, control resumes
# at whatever stale return-site was on the stack (e.g. inside the
# playthrough-1 branch of `start`), and the story derails into
# act 2 / Just Monika on its own.
#
# Fix: purge the whole return stack, then enter a wrapper label that
# CALLS the chapter and replays the exact vanilla continuation.
# =====================================================================

label mod_jump_dispatch:
    python:
        renpy.block_rollback()
        while renpy.get_return_stack():
            renpy.pop_call()
        renpy.jump(store.mod_target)

# ---------- playthrough 0 (act 1) ----------
label mod_ch0_main:
    $ chapter = 0
    call ch0_main
    call poem
    $ chapter = 1
    call ch1_main
    jump mod_pt0_after_ch1

label mod_ch1_main:
    $ chapter = 1
    call ch1_main
    jump mod_pt0_after_ch1

label mod_pt0_after_ch1:
    call poemresponse_start
    call ch1_end
    call poem
    $ chapter = 2
    call ch2_main
    jump mod_pt0_after_ch2

label mod_ch2_main:
    $ chapter = 2
    call ch2_main
    jump mod_pt0_after_ch2

label mod_pt0_after_ch2:
    call poemresponse_start
    call ch2_end
    call poem
    $ chapter = 3
    call ch3_main
    jump mod_pt0_after_ch3

label mod_ch3_main:
    $ chapter = 3
    call ch3_main
    jump mod_pt0_after_ch3

label mod_pt0_after_ch3:
    call poemresponse_start
    call ch3_end
    $ chapter = 4
    call ch4_main
    jump mod_pt0_after_ch4

label mod_ch4_main:
    $ chapter = 4
    call ch4_main
    jump mod_pt0_after_ch4

label mod_ch5_main:
    $ chapter = 5
    call ch5_main
    jump mod_pt0_after_ch4

label mod_pt0_after_ch4:
    $ chapter = 5
    call ch5_main
    call endgame
    return

# ---------- playthrough 1 (Sayori's fate) ----------
label mod_ch10_main:
    call ch10_main
    jump playthrough2

# ---------- playthrough 2 (act 2) ----------
label mod_ch20_main:
    call ch20_main
    jump playthrough2

label mod_ch21_main:
    $ chapter = 1
    call ch21_main
    jump mod_pt2_after_ch21

label mod_pt2_after_ch21:
    call poemresponse_start
    call ch21_end
    call poem (False)
    $ chapter = 2
    call ch22_main
    jump mod_pt2_after_ch22

label mod_ch22_main:
    $ chapter = 2
    call ch22_main
    jump mod_pt2_after_ch22

label mod_pt2_after_ch22:
    call poemresponse_start
    call ch22_end
    call poem (False)
    $ chapter = 3
    call ch23_main
    jump mod_pt2_after_ch23

label mod_ch23_main:
    $ chapter = 3
    call ch23_main
    jump mod_pt2_after_ch23

label mod_pt2_after_ch23:
    if y_appeal >= 3:
        call poemresponse_start2
    else:
        call poemresponse_start
    call ch23_end
    return

# ---------- playthrough 3 (Just Monika) ----------
label mod_ch30_main:
    call ch30_main
    return
