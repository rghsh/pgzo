"""Class library from the introductory book.

This module exports two classes ``Stage`` and ``GameObj`` and
a global object ``mouse_state``.

Also this module implements all hook methods of Pygame Zero,
i. e. ``draw``, ``update``, ``on_mouse_down``, 
``on_mouse_up``, ``on_mouse_move``, ``on_key_down``, 
``on_key_up``. All hook methods delegate to the
current stage's respective methods (see ``Stage.show()`` 
and ``Stage.current``).
"""

import sys
import math
import functools
import warnings

import pygame

from pgzero.actor import Actor
from pgzero.constants import mouse
from pgzero import spellcheck

__version__ = "0.9"
__author__ = "Robert Garmann"


class _MetaPGZ(type):
    @property
    def screen(cls):
        return cls.get_builtins_mod().screen

    @property
    def WIDTH(cls):
        return cls.get_builtins_mod().WIDTH

    @property
    def HEIGHT(cls):
        return cls.get_builtins_mod().HEIGHT

    @property
    def TITLE(cls):
        return cls.get_builtins_mod().TITLE


class _PGZ(object, metaclass=_MetaPGZ):
    """Helper class gives access to builtin pgz properties.

    These properties are provided by Pygame Zero to the main module.

    Usage example: ``_PGZ.screen``

    see also https://stackoverflow.com/a/3203434
    """

    the_pgz_builtins_mod = None  # class attribute that caches the main module

    @classmethod
    def get_builtins_mod(cls):
        if cls.the_pgz_builtins_mod is None:
            if getattr(sys, '_pgzrun', None):
                # We're running with the pgzrun runner
                modname = "pgzero.builtins"
                # Search for the module whose name is pgzero.builtins
                # but whose key is different. That is the real main module:
                for k, v in sys.modules.items():
                    if v.__name__ == "pgzero.builtins" \
                            and k != "pgzero.builtins":
                        modname = k
                        break
                cls.the_pgz_builtins_mod = sys.modules[modname]
            else:
                cls.the_pgz_builtins_mod = sys.modules['__main__']

        return cls.the_pgz_builtins_mod


_ALL_PREVIOUS_TYPES = []
"""Collects type names that have been spelling-warned."""


def _call_base_and_sub_op(a, basecls, op_name, **kwargs):
    """Call ``op_name`` on ``a`` for ``basecls`` AND then for ``a`` itself.

    This function relieves a subclass of ``basecls`` from calling super-methods
    in overwritten methods. Also this function can detect object (<locals>)
    properties in ``a`` of the same name ``op_name``, which is handled as if the
    object ``a`` would be of a subclass-type overriding ``op_name``.

    This allows the book to introduce methods as simple attributes in objects
    that easlily can be added to an object.
    """

    debug = False

    if debug:
        print("v" * 40)
        print("start of _call_base_and_sub_op is going to call ", op_name)

    # call method of base class first:
    baseop = basecls.__dict__.get(op_name)
    baseop(a, **kwargs)

    #
    # search for overwriting method in a's class or in a itself:
    #
    is_class_method = False
    if type(a) is basecls:
        # there might be a function object in the object ...
        op = getattr(a, op_name, None)
        description = "object function"
        if op is not None:
            is_bound = hasattr(op, "__self__")
            if is_bound:
                # This is not an object function, but a class method
                op = None
    elif issubclass(type(a), basecls):
        # there might be a function object in a's class ...
        op = type(a).__dict__.get(op_name)
        description = "class method "
        is_class_method = True
    else:
        raise Exception("_call_base_and_sub_op: unexpected type")
    if op is not None:
        description += " " + op.__qualname__

    #
    # found?
    #
    if op is not None and callable(op):
        # Then call it
        code = op.__code__
        param_names = code.co_varnames[:code.co_argcount]
        d = {}  # argument list that will be passed to "op" below
        for k, v in kwargs.items():
            if k in param_names:
                # take a subset of "kwargs" that match any parameter in "op"
                d[k] = v
        if is_class_method:
            d["self"] = a
        else:
            is_bound = hasattr(getattr(a, op_name, None), "__self__")
            if not is_bound and \
                    len(param_names) > 0 and \
                    param_names[0] == "self":
                d["self"] = a

        if debug:
            print("   description=", description)
            print("   type(op)=", type(op))
            print("   basecls=", basecls.__qualname__)
            print("   op_name=", op_name)
            print(
                "   type(a)=", type(a), ", op=", op,
                ", param_names=", param_names, " kwargs=", kwargs, "d=", d)
        op(**d)
    else:
        # Otherwise give hints in spelling:
        type_name = type(a).__name__
        if type_name not in _ALL_PREVIOUS_TYPES:
            _ALL_PREVIOUS_TYPES.append(type_name)
            funcs = {}
            d = vars(type(a)).copy()
            d.update(vars(a))
            for name, val in d.items():
                if name in type(a).__dict__ and \
                        callable(val) and \
                        not isinstance(val, type):
                    funcs[name] = val
            if debug:
                print("    funcs=", funcs)

            c = []
            if isinstance(a, Stage):
                STAGE_HOOKS = [
                    'draw',
                    'update',
                    'on_key_down',
                    'on_key_up',
                    'on_mouse_down',
                    'on_mouse_up',
                    'on_mouse_move'
                ]
                for p in spellcheck.compare(funcs, STAGE_HOOKS):
                    c.append(p)
                # give hint that Stage class expects an update
                # instead of act method:
                if "act" in funcs:
                    c.append(("act", "update"))
            elif isinstance(a, GameObj):
                GAMEOBJ_HOOKS = [
                    'draw',
                    'act',
                    'on_key_down',
                    'on_key_up',
                    'on_mouse_down',
                    'on_mouse_up',
                    'on_mouse_move'
                ]
                for p in spellcheck.compare(funcs, GAMEOBJ_HOOKS):
                    c.append(p)
                # give hint that GameObj class expects an act
                # instead of update method:
                if "update" in funcs:
                    c.append(("update", "act"))

            for found, suggestion in c:
                print(
                    "Warning: found function named {found} in {type_name}, "
                    "did you mean {suggestion}?".format(
                        found=found,
                        type_name=type_name,
                        suggestion=suggestion))

    if debug:
        print("end of _call_base_and_sub_op is going to call ", op_name)
        print("^" * 40)


class MouseState:
    """The current state of the mouse."""

    _pressed = set()
    """The current button state. 

    This may as well be a class attribute - there's only one mouse.
    """

    _pos = (0, 0)

    _moved = False

    def __getattr__(self, bname):
        if bname == "pos":
            return self._pos

        if bname == "moved":
            result = self._moved
            self._moved = False
            return result

        try:
            button = mouse[bname.upper()]
        except AttributeError:
            raise AttributeError('The button "%s" does not exist' % bname)
        return button in self._pressed

    def _press(self, button):
        """Called by pgz to mark the button as pressed."""
        self._pressed.add(button)

    def _release(self, button):
        """Called by pgz to mark the button as released."""
        self._pressed.discard(button)

    def _set_pos(self, pos):
        """Called by pgz to set the current position."""
        if pos != self._pos:
            self._moved = True
        self._pos = pos

    def __getitem__(self, b):
        if isinstance(b, mouse):
            return b in self._pressed
        else:
            warnings.warn(
                "String lookup in mouse (eg. mouse[%r]) is "
                "deprecated." % b,
                DeprecationWarning,
                2
            )
            return getattr(self, b)


mouse_state = MouseState()
"""The current state of the mouse.

Each attribute represents a mouse button. For example, ::

    mouse_state.left

is ``True`` if the left button is depressed, and
``False`` otherwise.

By calling ::

    mouse_state.pos

the current mouse position will be returned.

In order to check, whether the mouse position has
changed since the last call, use ::

    mouse_state.moved

Note, that an immediately following call to
``mouse.moved`` will always return ``False``.
The value will be ``True`` after the next mouse movement.
"""


class Stage:
    """The game can consist of several stages.

    There is only one stage visible at the
    same time. All drawing and all updates
    of game state will be done in the active
    stage. A stage usually contains many
    game objects, that each perform individual
    ``draw`` and ``update`` operations.
    """

    current = None
    DEFAULT_EDGE = 0

    def __new__(typ, *args, **kwargs):
        result = object.__new__(typ, *args, **kwargs)
        result.game_objects = []
        return result

    def __init__(self, background_image=None):
        """Create an empty stage with a background.

        If ``background_image`` is ``None``, we draw a 
        white background.
        """
        self.background_image = background_image

    def show(self):
        """Make this stage the current stage."""
        Stage.current = self

    def is_on_stage(self, game_obj):
        """Check if ``game_obj`` is on this stage."""
        return game_obj.stage is self

    def count_game_objects(self, cls=object):
        """Return number of game objects of given class."""
        # https://stackoverflow.com/a/44351664
        def ilen(iterable):
            return functools.reduce(
                lambda sum, element: sum + 1,
                iterable,
                0)
        return ilen(self.get_game_objects(cls))

    def get_game_objects(self, cls=object):
        """Iterate this stage's game objects of given class."""
        def pred(a):
            return isinstance(a, cls) and \
                hasattr(a, "stage") and \
                a.stage is not None
        # The filter needs to include an "on stage"-check, since
        # "get_game_objects" could be used in a far outer loop e. g.
        # in "update", where actors at the start of the list "killed"
        # actors at the end of the list from the stage.
        # Hence, when actors at the end of the list come into play,
        # they may already be off the stage.
        return filter(pred, self.game_objects)

    def _remove_game_object(self, game_obj):
        if not isinstance(game_obj, GameObj):
            raise Exception(
                "The remove_game_object method does not accept " +
                type(game_obj) +
                "-parameter")
        self.game_objects.remove(game_obj)

    def leave_all(self, cls=object):
        """Let all game objects of given class leave this stage."""
        if not isinstance(cls, type):
            raise Exception(
                "The leave_all method does not accept " + type(cls) +
                "-parameter")
        # make a copy to prevent concurrent modification when iterating
        objs = list(self.get_game_objects(cls))
        for item in objs:
            item.leave_stage()

    def is_beyond_edge(self, pos, edge=(DEFAULT_EDGE, DEFAULT_EDGE)):
        """Check, if ``pos`` is beyond the stage's edges.

        With the ``edge`` parameter you can define a tuple of x,y
        coordinates which makes the stage smaller on each of the
        four sides.
        """
        if pos[0] < edge[0] or pos[0] > _PGZ.WIDTH - edge[0]:
            return True
        if pos[1] < edge[1] or pos[1] > _PGZ.HEIGHT - edge[1]:
            return True
        return False

    def _call_all_gameobj_and_sub_op(self, op_name, **kwargs):
        """Helper."""
        for a in self.get_game_objects():
            _call_base_and_sub_op(a=a,
                                  basecls=GameObj,
                                  op_name=op_name,
                                  **kwargs)

    def draw(self):
        """Draw Background and dispatch ``draw`` call to all game objects."""
        if self.background_image is None:
            _PGZ.screen.fill("white")
        else:
            _PGZ.screen.blit(self.background_image, (0, 0))  # background image
        self._call_all_gameobj_and_sub_op("draw")

    def update(self):
        """Dispatch ``act`` call to all game objects."""
        self._call_all_gameobj_and_sub_op("act")

    def on_mouse_down(self, pos, button):
        """Dispatch ``on_mouse_down`` call to all game objects."""
        self._call_all_gameobj_and_sub_op(
            "on_mouse_down", pos=pos, button=button)

    def on_mouse_up(self, pos, button):
        """Dispatch ``on_mouse_up`` call to all game objects."""
        self._call_all_gameobj_and_sub_op(
            "on_mouse_up", pos=pos, button=button)

    def on_mouse_move(self, pos, rel, buttons):
        """Dispatch ``on_mouse_move`` call to all game objects."""
        self._call_all_gameobj_and_sub_op(
            "on_mouse_move", pos=pos, rel=rel, buttons=buttons)

    def on_key_up(self, key, mod):
        """Dispatch ``on_key_up`` call to all game objects."""
        self._call_all_gameobj_and_sub_op("on_key_up", key=key, mod=mod)

    def on_key_down(self, key, mod, unicode):
        """Dispatch ``on_key_down`` call to all game objects."""
        self._call_all_gameobj_and_sub_op(
            "on_key_down", key=key, mod=mod, unicode=unicode)


def _call_current_stage_and_sub_op(op_name, **kwargs):
    """Helper."""
    if Stage.current is not None:
        _call_base_and_sub_op(
            a=Stage.current,
            basecls=Stage,
            op_name=op_name,
            **kwargs)

            
# The following methods are the PGZero specific
# way to draw and to update the game state. We delegate
# all tasks to the current stage:


def draw():
    """Pygame Zero global hook method."""
    _call_current_stage_and_sub_op("draw")


def update():
    """Pygame Zero global hook method."""
    _call_current_stage_and_sub_op("update")


def on_mouse_down(pos, button):
    """Pygame Zero global hook method."""
    mouse_state._press(button)
    mouse_state._set_pos(pos)
    _call_current_stage_and_sub_op("on_mouse_down", pos=pos, button=button)


def on_mouse_up(pos, button):
    """Pygame Zero global hook method."""
    mouse_state._release(button)
    mouse_state._set_pos(pos)
    _call_current_stage_and_sub_op("on_mouse_up", pos=pos, button=button)


def on_mouse_move(pos, rel, buttons):
    """Pygame Zero global hook method."""
    mouse_state._set_pos(pos)
    _call_current_stage_and_sub_op(
        "on_mouse_move", pos=pos, rel=rel, buttons=buttons)


def on_key_up(key, mod):
    """Pygame Zero global hook method."""
    _call_current_stage_and_sub_op("on_key_up", key=key, mod=mod)


def on_key_down(key, mod, unicode):
    """Pygame Zero global hook method."""
    _call_current_stage_and_sub_op(
        "on_key_down", key=key, mod=mod, unicode=unicode)


class GameObj(Actor):
    """An actor on stage.

    On the current stage there can be several
    *game objects*. A game object has a position
    and a rotation angle, a current speed
    and a current image.

    A game object has got an ``act`` method that
    takes care of all event processing and
    other game state manipulations. Also
    there is a ``draw`` method that will draw the
    image onto the screen. The ``act`` method
    usually is overridden by subclasses in
    order to add game specific behaviour. The
    ``draw`` method should only be overridden in
    order to tweak visual appearance of
    the game object.
    """

    DEFAULT_SPEED = 5
    """Default speed in pixels."""
    
    MIN_SPEED = -10
    """Minimum speed in pixels."""

    MAX_SPEED = 10
    """Maximum speed in pixels."""

    DEFAULT_IMAGE = pygame.image.frombuffer(
        b'\x00\x00\x00\x00', (1, 1), "RGBA")
    """A 1x1 pixel image with a transparent background."""

    def __new__(typ, *args, **kwargs):
        result = Actor.__new__(typ)
        # Actor's image is mandatory, because it bases
        # all _rect-operations on it.
        # So we need to initialize a default image:
        GameObj.__init__(result)
        return result

    def __init__(self,
                 image=None,
                 pos=None,
                 speed=None,
                 orbit_center=None,
                 stage=None,
                 center_drawing_color=None,
                 pos_drawing_color=None,
                 rect_drawing_color=None,
                 **kwargs):
        """Create a game object with ``image`` and ``center`` position.

        In contrast with ``Actor`` all parameters are optional in
        order to support client-side initialization by setting
        attributes.

        When an ``image`` is missing, we use a 1x1 pixel transparent
        image instead.

        If ``center_drawing_color``, ``pos_drawing_color``, or
        ``rect_drawing_color`` are given, then this class will
        draw a center point, a coordinate tuple, or
        a bounding rectangle respectively.
        """
        Actor.__init__(self, image, pos=pos, **kwargs)
        if speed is None:
            speed = self.DEFAULT_SPEED
        self.speed = speed
        self.orbit_center = orbit_center
        self.total_orbit_angle = 0
        self.stage = stage
        self.rect_drawing_color = rect_drawing_color
        self.center_drawing_color = center_drawing_color
        self.pos_drawing_color = pos_drawing_color

    @property
    def image(self):
        """Image name or ``None``."""
        # https://stackoverflow.com/questions/1021464/how-to-call-a-property-of-the-base-class-if-this-property-is-being-overwritten-i/1021484
        return Actor.image.fget(self)

    @image.setter
    def image(self, image):
        """Set the image name.

        This overwrites an ``Actor`` property because of two reasons.
        First we want to be able to pass ``image=None``. This property
        accepts a ``None`` parameter and uses a 1x1 pixel transparent image.
        Second ``Actor`` is buggy when setting the image to a rotated actor.
        In that case the overwriting setter calculates the new
        image depending on the current rotation.
        """
        if image is None:
            # Unfortunately we need to access private attributes:
            self._image_name = None
            self._orig_surf = self._surf = GameObj.DEFAULT_IMAGE
            self._update_pos()
        else:
            # https://stackoverflow.com/questions/1021464/how-to-call-a-property-of-the-base-class-if-this-property-is-being-overwritten-i/1021484
            Actor.image.fset(self, image)

        # adjust image rotation by setting angle again
        Actor.angle.fset(self, self.angle)

    @property
    def rect(self):
        """The rectangle around this object."""
        return pygame.Rect(self.topleft, (self.width, self.height))

    @property
    def mask(self):
        """An image mask for collision detection."""
        # Unfortunately pgzero's Actor does not exhibit the image surface as
        # public property. So we need to access the private _surf attribute.
        return pygame.mask.from_surface(self._surf)

    def overlaps(self, other):
        """Check for pixel-exact overlap of two game objects."""
        if self.colliderect(other):
            ox = round(self.topleft[0] - other.topleft[0])
            oy = round(self.topleft[1] - other.topleft[1])
            offset = (ox, oy)
            if other.mask.overlap(self.mask, offset) is not None:
                return True
        return False

    def draw(self):
        """Draw image and additional artifacts.

        This additionally draws a center point, a coordinate tuple, or
        a bounding rectangle, if the respective attributes have
        been set to a color.
        """
        Actor.draw(self)
        if getattr(self, "center_drawing_color", None) is not None:
            _PGZ.screen.draw.filled_circle(self.center,
                                           5, self.center_drawing_color)
        if getattr(self, "rect_drawing_color", None) is not None:
            _PGZ.screen.draw.rect(self.rect, self.rect_drawing_color)
        if getattr(self, "pos_drawing_color", None) is not None:
            _PGZ.screen.draw.text(
                ("(%d,%d)" % (round(self.x), round(self.y))),
                midtop=(self.center),
                color=self.pos_drawing_color)

    def act(self):
        """Act - empty method, game objects have no default action."""
        pass

    def on_mouse_down(self, pos, button):
        """Empty method, game objects have no default event handling."""
        pass

    def on_mouse_up(self, pos, button):
        """Empty method, game objects have no default event handling."""
        pass

    def on_mouse_move(self, pos, rel, buttons):
        """Empty method, game objects have no default event handling."""
        pass

    def on_key_up(self, key, mod):
        """Empty method, game objects have no default event handling."""
        pass

    def on_key_down(self, key, mod, unicode):
        """Empty method, game objects have no default event handling."""
        pass

    def appear_on_stage(self, stage):
        """Put this game object on a stage.

        If this game object currently is on a stage, it is taken out
        first by automatically calling leave_stage.
        """
        if self.stage is not None:
            self.leave_stage()
        stage.game_objects.append(self)
        self.stage = stage

    def leave_stage(self):
        """This game object leaves it's current stage.

        If this object is not on a stage, a ``RuntimeError``
        is raised.
        """
        if self.stage is None:
            raise RuntimeError(
                "This game object has not been added to a stage")
        self.stage._remove_game_object(self)
        self.stage = None

    def is_beyond_stage_edge(self, edge=(30, 30)):
        """Test if we are beyond the edges of the stage.

        Return ``True`` is we are.
        """
        if self.stage is None:
            raise Exception(
                "This game object has not been added to a stage")
        return self.stage.is_beyond_edge((self.x, self.y), edge=edge)

    def turn(self, angle=1):
        """Turn ``angle`` degrees towards the left (counter clockwise)."""
        self.angle += angle

    def move(self, distance=None):
        """Move forward in the current direction."""
        hop_x, hop_y = self.next_hop(distance)
        self.x += hop_x
        self.y += hop_y

    def next_hop(self, distance=None):
        """Get (x,y) tuple where a ``move(distance)`` call would finish."""
        rad = math.radians(self.angle)
        if distance is None:
            distance = self.speed
        return (math.cos(rad) * distance, - math.sin(rad) * distance)

    def can_move(self,
                 distance=None,
                 edge=(Stage.DEFAULT_EDGE, Stage.DEFAULT_EDGE)):
        """Check, if we can move forward without leaving the stage.

        If we get beyond one of the edges of the stage, return ``False``.
        """
        if self.stage is None:
            raise RuntimeError(
                "This game object has not been added to a stage")
        move = self.next_hop(distance)
        return not self.stage.is_beyond_edge(
            (self.x + move[0], self.y + move[1]), edge=edge)

    def speed_up(self):
        """Increment current speed by 0.1.

        The resulting speed is ceiled by a maximum speed.
        """
        self.speed += 0.1
        if self.speed > self.MAX_SPEED:
            self.speed = self.MAX_SPEED

    def slow_down(self):
        """Increment current speed by -0.1.

        The resulting speed is floored by a minimum (negative) speed.
        """
        self.speed -= 0.1
        if self.speed < self.MIN_SPEED:
            self.speed = self.MIN_SPEED

    def orbit(self, angle):
        """Orbit around ``orbit_center`` attribute by ``angle`` degrees.

        Orbit goes towards the left (counter clockwise).
        """
        self.total_orbit_angle += angle
        x = self.x - self.orbit_center.x
        y = self.y - self.orbit_center.y
        new_angle_radians = math.radians(
            math.degrees(math.atan2(y, x)) + angle)
        radius = math.sqrt(x*x + y*y)
        self.x = self.orbit_center.x + radius * math.cos(new_angle_radians)
        self.y = self.orbit_center.y + radius * math.sin(new_angle_radians)

    def full_orbits(self):
        """Return the accumulated full orbits.

        A full orbit is 360 degrees.
        """
        return math.floor(self.total_orbit_angle / 360)
