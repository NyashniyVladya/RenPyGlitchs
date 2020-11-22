
init -100 python in _glitch_setting:

    import random
    import store
    from store import (
        NoRollback,
        Fixed,
        Solid
    )

    class _Glitch(renpy.Displayable, NoRollback):

        __author__ = "Vladya"
        __version__ = "2.0.1"

        def __init__(self, child=None, glitch_strength=.05, _fps=5., **kwargs):

            """
            :child:
                Изображение, к которому применяется эффект.
            :glitch_strength:
                Сила искажений. Насколько будет "потряхивать" изображение.
                От .0 до 1. включительно.
            :_fps:
                Приблизительная частота смены картинки.
                Будет рандомизирована.
            :min_crop_width:
                Минимальное значение ширины вырезаемого фрагмента,
                для рандомной выборки.
                Выражается float значением от .0 (не включительно) до 1.,
                которое будет интерпретировано, как процент от размера
                исходного изображения.
            :max_crop_width:
                Максимальное значение ширины вырезаемого фрагмента.
                Выражается float значением от минимального до 1..
                Если передан только один параметр,
                второй приравнивается к нему.
            :min_crop_height:
                То же самое, что и 'min_crop_width', но для высоты.
            :max_crop_height:
                То же самое, что и 'max_crop_width', но для высоты.
            :color_range1:
                Нижний диапазон выборки цвета фрагемента.
                Итоговый цвет будет выбран по следующему принципу:
                    Допустим 'color_range1' выглядит как:
                        (128, 128, 128, 255)
                    А 'color_range2' как:
                        (0, 255, 0, 255)
                    Итоговый цвет будет выбран по следующей логике:
                        ((0-128), (128-255), (0-128), 255)
                        Где (0-128) случайное число в диапазоне от 0 до 128,
                        представляющее собой соответствующий тон
                        в диапазоне RGB.
            :color_range2:
                Верхний диапазон выборки цвета.
            """

            super(_Glitch, self).__init__()
            self.__child = None
            if child is not None:
                child = renpy.easy.displayable(child)
                if not isinstance(child, renpy.display.core.Displayable):
                    raise TypeError(__("Передан не 'displayable' объект."))
                self.__child = child

            self.__init_kwargs = {
                "glitch_strength": glitch_strength,
                "_fps": _fps
            }
            self.__init_kwargs.update(kwargs)

            self.glitch_strength = glitch_strength

            crop_params = {}
            for d in ("width", "height"):
                min_value = kwargs.pop("min_crop_{0}".format(d), None)
                max_value = kwargs.pop("max_crop_{0}".format(d), None)
                if (min_value is None) and (max_value is None):
                    if d == "width":
                        crop_params[d] = {"min": .25, "max": .75}
                    else:
                        crop_params[d] = {"min": .05, "max": .15}
                    continue
                if min_value is None:
                    min_value = max_value
                elif max_value is None:
                    max_value = min_value
                min_value, max_value = map(float, (min_value, max_value))
                if not (.0 < min_value <= max_value <= 1.):
                    raise ValueError(
                        __("Диапазон {0}-{1} некорректен.").format(
                            min_value,
                            max_value
                        )
                    )
                crop_params[d] = {"min": min_value, "max": max_value}

            self.__crop_params = crop_params

            color_range1 = kwargs.pop("color_range1", None)
            color_range2 = kwargs.pop("color_range2", None)
            if color_range1 is None:
                color_range1 = color_range2
            elif color_range2 is None:
                color_range2 = color_range1
            self.__color_range = (
                renpy.color.Color((color_range1 or "0000")),
                renpy.color.Color((color_range2 or "#fff8")),
            )

            self.__fps = float(_fps)
            if self.__fps <= .0:
                raise ValueError(__("Некорректное значение '_fps'."))

        @property
        def glitch_strength(self):
            return self.__glitch_strength

        @glitch_strength.setter
        def glitch_strength(self, new_value):
            self.__glitch_strength = float(new_value)
            if not (.0 <= self.__glitch_strength <= 1.):
                raise ValueError(__("Некорректное значение 'glitch_strength'"))

        def __call__(self, child):
            """
            Для полноценной работы в качестве "at".
            """
            kwargs = self.__init_kwargs.copy()
            return _Glitch(child, **kwargs)

        def event(self, ev, x, y, st):
            if self.__child:
                return self.__child.event(ev, x, y, st)

        def visit(self):
            if self.__child:
                return [self.__child]
            return []

        def _get_color(self):
            return renpy.color.Color(
                tuple(
                    map(lambda x: random.uniform(*x), zip(*self.__color_range))
                )
            )

        def _get_rand_crop_area(self, x_size, y_size):

            x_size, y_size = map(float, (x_size, y_size))

            _range = self.__crop_params["width"]
            crop_width = x_size * random.uniform(_range["min"], _range["max"])
            if crop_width < 1.:
                crop_width = 1.

            _range = self.__crop_params["height"]
            crop_height = y_size * random.uniform(_range["min"], _range["max"])
            if crop_height < 1.:
                crop_height = 1.

            crop_x = random.uniform(.0, (x_size - crop_width))
            crop_y = random.uniform(.0, (y_size - crop_height))

            return (crop_x, crop_y, crop_width, crop_height)

        @staticmethod
        def get_color_alphamask_from_surface(surface, color, *render_args):

            surface = surface.subsurface((0, 0, surface.width, surface.height))
            color = renpy.color.Color(color)

            bottom = renpy.render(Fixed(), *render_args)
            color_mask = renpy.render(Solid(color), *render_args)

            result_render = renpy.Render(surface.width, surface.height)

            alphamask_render = renpy.Render(surface.width, surface.height)
            alphamask_render.operation = renpy.display.render.IMAGEDISSOLVE
            alphamask_render.operation_alpha = 1.
            alphamask_render.operation_complete = .5
            alphamask_render.operation_parameter = 256

            alphamask_render.blit(surface, (0, 0))
            alphamask_render.blit(bottom, (0, 0))
            alphamask_render.blit(color_mask, (0, 0))

            result_render.blit(surface, (0, 0))
            result_render.blit(alphamask_render, (0, 0))

            return result_render

        @staticmethod
        def zoom_surface(surface, xzoom, yzoom=None):

            surface = surface.subsurface((0, 0, surface.width, surface.height))
            if yzoom is None:
                yzoom = xzoom

            xzoom, yzoom = map(float, (xzoom, yzoom))
            width, height = map(float, surface.get_size())
            width *= xzoom
            height *= yzoom
            width, height = map(lambda x: (abs(int(x)) or 1), (width, height))

            result_render = renpy.Render(width, height)

            surface.zoom(xzoom, yzoom)
            surface = surface.subsurface((0, 0, width, height))

            result_render.blit(surface, (0, 0))

            return result_render

        def divide(self, surface, number_of_elements, *render_args):

            """
            Делит текстуру на фрагменты
            """

            surface = surface.subsurface((0, 0, surface.width, surface.height))
            w, h = map(float, surface.get_size())
            result_render = renpy.Render(*map(int, (w, h)))

            for _i in xrange(number_of_elements):

                crop_x, crop_y, crop_w, crop_h = self._get_rand_crop_area(w, h)
                subsurface = surface.subsurface(
                    tuple(map(int, (crop_x, crop_y, crop_w, crop_h)))
                )

                subsurface = self.get_color_alphamask_from_surface(
                    subsurface,
                    self._get_color(),
                    *render_args
                )

                xzoom_addition = random.uniform(.0, 1.)
                yzoom_addition = random.uniform((-1.), .0)

                xzoom = ((1. + (xzoom_addition * self.glitch_strength)) or .1)
                yzoom = ((1. + (yzoom_addition * self.glitch_strength)) or .1)
                subsurface = self.zoom_surface(subsurface, xzoom, yzoom)

                if random.random() < .5:
                    _n = int((float(number_of_elements) / 10.))
                    if _n:
                        #  Рекуррентно делим часть на ещё более мелкие части.
                        subsurface = self.divide(subsurface, _n, *render_args)

                x = (crop_x + (crop_w * .5)) - (subsurface.width * .5)
                y = (crop_y + (crop_h * .5)) - (subsurface.height * .5)

                xoffet = subsurface.width * random.uniform((-1.), 1.)
                yoffet = subsurface.height * random.uniform((-1.), 1.)

                xoffet *= self.glitch_strength
                yoffet *= self.glitch_strength

                x += xoffet
                y += yoffet

                x, y = map(int, (x, y))
                result_render.blit(subsurface, (x, y))

            return result_render

        def render(self, *render_args):
            if not self.__child:
                return renpy.Render(1, 1)
            child_render = renpy.render(self.__child, *render_args)
            _num = random.randint(15, 50)
            result_render = self.divide(child_render, _num, *render_args)
            _redraw_time = (1. / self.__fps) * random.uniform(.75, 1.25)
            renpy.redraw(self, _redraw_time)
            return result_render

    setattr(store, "Glitch", _Glitch)
