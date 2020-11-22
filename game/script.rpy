
init:

    image eileen happy = "eileen happy.png"
    image eileen vhappy = "eileen vhappy.png"
    image eileen happy glitch = Glitch("eileen happy.png")
    define e = Character(_("Эйлин"), image="eileen")

    image lucy mad = "lucy mad.png"
    define l = Character(_("Люси"), image="lucy")


label start:
    window hide
    scene expression "#888"
    show eileen happy glitch at left
    e "Стандартные параметры. Можно объявить изображение с параметрами заранее, как в этом примере, а можно использовать через \"at\"."
    show eileen happy at Glitch(_fps=1000.)
    e "Ускорим анимацию."
    show eileen happy at Glitch(_fps=1000., glitch_strength=.3)
    e "Усилим эффект."
    show eileen happy at Glitch(_fps=1000., glitch_strength=.3, color_range1="#0a00", color_range2="0f0")
    e "Включим разброс исключительно в области зелёного цвета."
    pause 1.
    show lucy mad at Glitch(_fps=20., color_range1="c00a", color_range2="f00", glitch_strength=.5)
    l "[e], что ты делаешь с диалоговым окном?"
    show layer screens at Glitch(glitch_strength=.75)
    e vhappy "А что я с ним делаю?"
    $ ui.interact()
    return
