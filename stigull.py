### NOTE: Due to font weirdness, the scenes in this file
###       only produce the correct logo when rendered on macos.
###       On other operating systems, the contour integral sign
###       is not the same (it is rendered using Pango, not TeX).
###       My working theory is that most fonts do not define
###       the unicode character "∮" (U+222E), and so the operating
###       system defaults to some fallback font.
###       I'm not sure what this fallback font is in macos.
###       My research suggests it should be Helvetica Neue
###       but other sources suggest otherwise (namely 
###       https://codepen.io/MJLueck/pen/BQBREQ).
###       I have been unable to work around this issue with
###       .svg and .png files, so for now it is best to
###       render these scenes in macos.

from manim import *

## For StigullLogoRec
# config.background_color = "#252525"
# config.pixel_width = 1920
# config.pixel_height = 1180
# config.format = "webm"
# config.movie_file_extension = '.' + config.format

## For StigullLogoPlain
# config.background_opacity = 0
# config.pixel_width = 512
# config.pixel_height = 512
# config.frame_height = 1
# config.frame_width = 1
# config.format = "png"

## For StigullProfilePlaceholder
config.background_color = "#252525"
config.pixel_width = 512
config.pixel_height = 512
config.frame_height = 1
config.frame_width = 1
config.format = "png"

####################################

sc = 0.05
xmin = 0.18 - sc
xmax = 1 - 0.18 + sc
Dx = xmax - xmin
ymin = 0.1
ymax = 0.7928 + 2.46*sc
Dy = ymax - ymin
ytext = 0.58 + 0.09 + 0.005
textpt = 2*132+16
textprop = (0.125 + 0.114) / Dy


class SierpinskiTriangle(VGroup):
    def __init__(self, depth, root_depth=0, **kwargs):
        super().__init__()
        self.depth = depth
        if depth == 0:
            root = Triangle(
                stroke_opacity=0, 
                stroke_color=WHITE,
                fill_opacity=1,
                fill_color=WHITE, 
                stroke_width=0,
                **kwargs
            )
            root.rotate(60*DEGREES)
            root.stretch_to_fit_width(Dx/Dy*root.height)
            self.add(root)
        elif depth == root_depth:
            self.add(SierpinskiTriangle(root_depth, **kwargs))
        else:
            self.left = SierpinskiTriangle(depth-1, **kwargs)
            self.right = SierpinskiTriangle(depth-1, **kwargs)
            self.bottom = SierpinskiTriangle(depth-1, **kwargs)
            root = SierpinskiTriangle(0)
            for tri, coord in zip([self.left, self.right, self.bottom], [root.get_corner(UL), root.get_corner(UR), root.get_bottom()]):
                tri.scale(0.5, about_point=coord)
            self.add(*self.left, *self.right, *self.bottom)
        self.move_to(ORIGIN)

    def get_groups(self, root_depth=0):
        k = 3**root_depth
        yield VGroup(*self.submobjects[:k])
        last = k
        while k < len(self.submobjects):
            for m in range(2):
                yield VGroup(
                    *self.submobjects[last + m*k : last + (m+1)*k]
                )
            last += 2*k
            k *= 3
            

class StigullLogoRec(Scene):
    def construct(self):
        n, r = 4, 4
        tri = SierpinskiTriangle(n+r, root_depth=r).scale(3)
        base = tri.copy().set_color(config.background_color)
        
        S = Text("\u222E", font="Arial")
        S.scale_to_fit_height(textprop * tri.height)
        S.move_to((ytext - ymin)/Dy*tri.get_top() + (ymax - ytext)/Dy*tri.get_bottom())
        S.rotate((20*(1+sc))*DEGREES)

        text = Tex("STIGULL")
        text.scale_to_fit_width(tri.width)
        text.next_to(tri, UP)

        VGroup(base, tri, S, text).move_to(ORIGIN)

        ulcorner, urcorner, dcorner = tri.get_corner(UL), tri.get_corner(UR), tri.get_bottom()
        uldist = np.cross(urcorner - dcorner, ulcorner - dcorner)[2] / np.linalg.norm(urcorner - dcorner)
        tri.scale(2**n, about_point=ulcorner)
        base.scale(2**n, about_point=ulcorner)

        self.remove(tri)
        triparts = VGroup()

        for t in tri.get_groups(r):
            self.add(t)
            triparts.add(t)
            t.add_updater(
                lambda t: t.set_opacity(
                    1 + np.cross(urcorner - dcorner, t.get_bottom() - dcorner)[2] / (np.linalg.norm(urcorner - dcorner) * uldist)
                )
            )

        tri = triparts

        S0, text0 = S.copy(), text.copy()
        self.play(*[ApplyMethod(x.scale, 1/2**n, {"about_point": ulcorner}) for x in (base, tri, S0, text0)], run_time=3)
        newtri = SierpinskiTriangle(n).scale(3).move_to(tri)
        self.play(Write(S), Write(text), FadeIn(newtri), FadeOut(text0))
        self.wait()

    
class StigullLoop(Scene):
    def construct(self):
        n = 4
        tri = SierpinskiTriangle(n).scale(3)
        # tri.move_to(config.bottom, aligned_edge=DOWN).shift(tri.height*UP)

        text = Tex("STIGULL")
        text.scale_to_fit_width(tri.width)
        text.next_to(tri, UP)
        self.add(text)

        VGroup(tri, text).move_to(ORIGIN)

        ulcorner, urcorner, dcorner = tri.get_corner(UL), tri.get_corner(UR), tri.get_bottom()
        uldist = np.cross(urcorner - dcorner, ulcorner - dcorner)[2] / np.linalg.norm(urcorner - dcorner)
        tri.scale(4, about_point=ulcorner)

        self.remove(tri)
        triparts = VGroup()

        for t in tri.get_groups(n-2):
            self.add(t)
            triparts.add(t)
            t.add_updater(
                lambda t: t.set_opacity(
                    1 + np.cross(urcorner - dcorner, t.get_bottom() - dcorner)[2] / (np.linalg.norm(urcorner - dcorner) * uldist)
                )
            )

        tri = triparts
        
        S = [None]*n
        for i in range(n):
            S[i] = Text("\u222E", font="Arial")
            S[i].scale_to_fit_height(textprop * tri.height)
            S[i].move_to((ytext - ymin)/Dy*tri.get_top() + (ymax - ytext)/Dy*tri.get_bottom())
            S[i].rotate((20*(1+sc))*DEGREES)
            S[i].scale(2**(i-n), about_point=ulcorner)

        S[-1].add_updater(
            lambda s: s.set_opacity(
                1 + np.cross(urcorner - dcorner, triparts[-1].get_bottom() - dcorner)[2] / (np.linalg.norm(urcorner - dcorner) * uldist)
            )
        )
        
        self.add(*S)

        self.play(
            ApplyMethod(tri.scale, 1/2, {"about_point": ulcorner}), 
            *[ApplyMethod(s.scale, 1/2, {"about_point": ulcorner}) for s in S], 
            rate_func=lambda t: 2 - 1/2**(t-1),
            run_time=3
        )


# Compile with: -s -r 512,512
class StigullLogoPlain(Scene):
    def construct(self):
        tri = SierpinskiTriangle(4)
        S = Text("\u222E", font="Arial")
        S.scale_to_fit_height(textprop * tri.height)
        S.move_to((ytext - ymin)/Dy*tri.get_top() + (ymax - ytext)/Dy*tri.get_bottom())
        S.rotate((20*(1+sc))*DEGREES)
        VGroup(tri, S).scale_to_fit_height(config.frame_height*0.95).move_to(ORIGIN)
        self.add(tri, S)


class StigullProfilePlaceholder(Scene):
    def construct(self):
        S = Text("\u222E", font="Arial")
        S.rotate((20*(1+sc))*DEGREES)
        S.scale_to_fit_height(config.frame_height*0.8).move_to(ORIGIN)
        self.add(S)