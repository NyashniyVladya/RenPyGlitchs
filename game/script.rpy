
init python:

    from random import Random
    from __builtin__ import map as fixMap

    class Glitch(renpy.Displayable, Random, NoRollback):

        def __init__(self, pic, speed_multipler=.5):
            super(Glitch, self).__init__()
            self.pic = renpy.easy.displayable(pic)
            self.cached_pics = []
            self.speed_multipler = float(speed_multipler)

        def visit(self):
            return [i[0] for i in self.cached_pics] + [self.pic]

        def create_cache(self):
            self.cached_pics = [self.get_random_recolor() for i in xrange(500)]

        def get_random_crop(self):
            width, height = fixMap(
                lambda x: self.rndInt((self.random() * x * .1)),
                self.base_size
            )
            width *= 10
            x, y = fixMap(
                lambda x: self.rndInt(self.uniform(.0, (x[1] - x[0]))),
                zip((width, height), self.base_size)
            )
            return (
                LiveCrop((x, y, width, height), self.pic),
                (x, y),
                (width, height)
            )

        def get_random_recolor(self):
            crop, pos, size = self.get_random_crop()
            return (
                Transform(
                    LiveComposite(
                        size,
                        (0, 0),
                        crop,
                        (0, 0),
                        AlphaMask(
                            Solid(
                                tuple(self.randint(0, 200) for i in xrange(4))
                            ),
                            crop
                        )
                    ),
                    xzoom=self.uniform(1., 1.5),
                    yzoom=self.uniform(.5, 1.),
                ),
                pos,
                size
            )

        @staticmethod
        def rndInt(val):
            return int(round(float(val)))

        def render(self, width, height, st, at):

            pic_rend = renpy.render(self.pic, width, height, st, at)
            w, h = self.base_size = fixMap(self.rndInt, pic_rend.get_size())
            if not self.cached_pics:
                self.create_cache()
            renderObj = renpy.Render(w, h)
            if self.randint(0, 9):
                renderObj.blit(pic_rend, (0, 0))
            for i in xrange(self.randint(0, 50)):
                pic, pos, old_size = self.choice(self.cached_pics)
                oldX, oldY = old_size
                surface = renpy.render(pic, width, height, st, at)
                sizeX, sizeY = surface.get_size()
                x, y = pos
                x -= self.rndInt((float((sizeX - oldX)) / 2.))
                y -= self.rndInt((float((sizeY - oldY)) / 2.))
                x += (sizeX * self.uniform(-.2, .2))
                renderObj.blit(
                    renpy.render(pic, width, height, st, at),
                    (x, y)
                )
            renpy.redraw(self, (self.random() * self.speed_multipler))
            return renderObj

init:
    image spok = "mr_spok.png"
    image spok glitch = Glitch("mr_spok.png")
    image lina = "un_nightmare_end.png"
    image lina glitch = Glitch("un_nightmare_end.png")
    image norilsk = "norilsk.png"
    image norilsk glitch = Glitch("norilsk.png")

label start:
    scene norilsk
    show spok:
        align (.3, 1.)
    with dissolve
    "Мистер Спок" "Я наконец-то переехал в Норильск! Город мечты!"
    show lina glitch:
        align (.7, 1.)
    "Норильская девочка" "Вы уже видели чёрную пургу, мистер Спок?.."
    show spok glitch
    "Мистер Спок" "Мать твою!"
    show norilsk glitch
    "Норильская девочка" "Хе, хе, хе..."
    return
