from manim import *

config.background_color = "#252525"
config.pixel_width = 1920
config.pixel_height = 1180

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
        super().__init__(**kwargs)
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


class StigullLogo(Scene):
    def construct(self):
        n = 4
        tri = SierpinskiTriangle(n).scale(3)
        # tri.move_to(config.bottom, aligned_edge=DOWN).shift(tri.height*UP)

        S = Text("\u222E", font="Arial")
        S.scale_to_fit_height(textprop * tri.height)
        S.move_to((ytext - ymin)/Dy*tri.get_top() + (ymax - ytext)/Dy*tri.get_bottom())
        S.rotate((20*(1+sc))*DEGREES)

        text = Tex("STIGULL")
        text.scale_to_fit_width(tri.width)
        text.next_to(tri, UP)

        VGroup(tri, S, text).move_to(ORIGIN)

        ulcorner, urcorner, dcorner = tri.get_corner(UL), tri.get_corner(UR), tri.get_bottom()
        uldist = np.cross(urcorner - dcorner, ulcorner - dcorner)[2] / np.linalg.norm(urcorner - dcorner)
        tri.scale(2**n, about_point=ulcorner)

        self.remove(tri)

        triparts = VGroup()

        for t in tri.get_groups():
            self.add(t)
            triparts.add(t)
            t.add_updater(
                lambda t: t.set_opacity(
                    1 + np.cross(urcorner - dcorner, t.get_bottom() - dcorner)[2] / (np.linalg.norm(urcorner - dcorner) * uldist)
                )
            )

        tri = triparts

        self.play(ApplyMethod(tri.scale, 1/2**n, {"about_point": ulcorner}), run_time=3)
        self.play(Write(S), Write(text))
        # for i, tr in enumerate(tri.get_groups()):
        #     for t in tr: 
        #         self.add(Tex(str(i), color=RED).move_to(t).scale(0.3))
        self.wait()


class StigullLogoRec(Scene):
    def construct(self):
        n, r = 4, 4
        tri = SierpinskiTriangle(n+r, root_depth=r).scale(3)
        # tri.move_to(config.bottom, aligned_edge=DOWN).shift(tri.height*UP)

        S = Text("\u222E", font="Arial")
        S.scale_to_fit_height(textprop * tri.height)
        S.move_to((ytext - ymin)/Dy*tri.get_top() + (ymax - ytext)/Dy*tri.get_bottom())
        S.rotate((20*(1+sc))*DEGREES)

        text = Tex("STIGULL")
        text.scale_to_fit_width(tri.width)
        text.next_to(tri, UP)

        VGroup(tri, S, text).move_to(ORIGIN)

        ulcorner, urcorner, dcorner = tri.get_corner(UL), tri.get_corner(UR), tri.get_bottom()
        uldist = np.cross(urcorner - dcorner, ulcorner - dcorner)[2] / np.linalg.norm(urcorner - dcorner)
        tri.scale(2**n, about_point=ulcorner)

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
        self.play(*[ApplyMethod(x.scale, 1/2**n, {"about_point": ulcorner}) for x in (tri, S0, text0)], run_time=3)
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
