from __future__ import annotations

from contextlib import nullcontext as does_not_raise

import numpy as np
import pytest
from femto.waveguide import coupler
from femto.waveguide import NasuWaveguide
from femto.waveguide import Waveguide


@pytest.fixture
def param() -> dict:
    p = {
        'scan': 6,
        'speed': 20.0,
        'y_init': 1.5,
        'z_init': 0.050,
        'speed_closed': 75,
        'samplesize': (100, 15),
        'depth': 0.035,
        'radius': 25,
        'pitch': 0.127,
        'int_dist': 0.005,
        'int_length': 0.0,
        'arm_length': 1.0,
        'ltrench': 1.5,
        'dz_bridge': 0.006,
    }
    return p


@pytest.fixture
def empty_wg(param) -> Waveguide:
    return Waveguide(**param)


def test_default_values() -> None:
    wg = Waveguide()
    assert wg.scan == int(1)
    assert wg.speed == float(1.0)
    assert wg.x_init == float(-2.0)
    assert wg.y_init == float(0.0)
    assert wg.z_init == float(0.035)
    assert wg.lsafe == float(2.0)
    assert wg.speed_closed == float(5.0)
    assert wg.speed_pos == float(0.5)
    assert wg.cmd_rate_max == int(1200)
    assert wg.acc_max == int(500)
    assert wg.samplesize == (100, 50)
    assert wg.depth == float(0.035)
    assert wg.radius == float(15)
    assert wg.pitch == float(0.080)
    assert wg.pitch_fa == float(0.127)
    assert wg.int_dist is None
    assert wg.int_length == float(0.0)
    assert wg.arm_length == float(0.0)
    assert wg.ltrench == float(0.0)
    assert wg.dz_bridge == float(0.007)


def test_wg_values(param) -> None:
    wg = Waveguide(**param)
    assert wg.scan == int(6)
    assert wg.speed == float(20.0)
    assert wg.x_init == float(-2.0)
    assert wg.y_init == float(1.5)
    assert wg.z_init == float(0.050)
    assert wg.lsafe == float(2.0)
    assert wg.speed_closed == float(75)
    assert wg.speed_pos == float(0.5)
    assert wg.cmd_rate_max == int(1200)
    assert wg.acc_max == int(500)
    assert wg.samplesize == (100, 15)
    assert wg.depth == float(0.035)
    assert wg.radius == float(25)
    assert wg.pitch == float(0.127)
    assert wg.pitch_fa == float(0.127)
    assert wg.int_dist == float(0.005)
    assert wg.int_length == float(0.0)
    assert wg.arm_length == float(1.0)
    assert wg.ltrench == float(1.5)
    assert wg.dz_bridge == float(0.006)


def test_wg_from_dict(param) -> None:
    wg = Waveguide.from_dict(param)
    assert wg.scan == int(6)
    assert wg.speed == float(20.0)
    assert wg.x_init == float(-2.0)
    assert wg.y_init == float(1.5)
    assert wg.z_init == float(0.050)
    assert wg.lsafe == float(2.0)
    assert wg.speed_closed == float(75)
    assert wg.speed_pos == float(0.5)
    assert wg.cmd_rate_max == int(1200)
    assert wg.acc_max == int(500)
    assert wg.samplesize == (100, 15)
    assert wg.depth == float(0.035)
    assert wg.radius == float(25)
    assert wg.pitch == float(0.127)
    assert wg.pitch_fa == float(0.127)
    assert wg.int_dist == float(0.005)
    assert wg.int_length == float(0.0)
    assert wg.arm_length == float(1.0)
    assert wg.ltrench == float(1.5)
    assert wg.dz_bridge == float(0.006)


def test_z_init(param) -> None:
    param['z_init'] = None
    param['depth'] = 0.05
    wg = Waveguide(**param)
    assert wg.z_init == float(0.05)


def test_scan(param) -> None:
    param['scan'] = 1.2
    with pytest.raises(ValueError):
        Waveguide(**param)


def test_dy_bend_pitch_error(param) -> None:
    wg = Waveguide(**param)
    wg.pitch = None
    with pytest.raises(ValueError):
        print(wg.dy_bend)

    param['pitch'] = None
    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        print(wg.dy_bend)


def test_dy_bend_int_dist_error(param) -> None:
    wg = Waveguide(**param)
    wg.int_dist = None
    with pytest.raises(ValueError):
        print(wg.dy_bend)

    param['int_dist'] = None
    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        print(wg.dy_bend)


def test_dy_bend(param) -> None:
    wg = Waveguide(**param)
    assert wg.dy_bend == 0.061


# TODO: add test cases
def test_dx_bend_radius_error(param) -> None:
    wg = Waveguide(**param)
    wg.radius = None
    with pytest.raises(ValueError):
        print(wg.dx_bend)

    param['radius'] = None
    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        print(wg.dx_bend)


# TODO: add test cases
def test_dx_bend(param) -> None:
    wg = Waveguide(**param)
    assert pytest.approx(wg.dx_bend) == 2.469064


def test_dx_acc_none(param) -> None:
    param['int_length'] = None
    wg = Waveguide(**param)
    with pytest.raises(TypeError):
        print(wg.dx_coupler)


# TODO: add test cases
def test_dx_acc(param) -> None:
    wg = Waveguide(**param)
    assert pytest.approx(wg.dx_coupler) == 4.938129


def test_dx_acc_int_l(param) -> None:
    param['int_length'] = 2
    wg = Waveguide(**param)
    assert pytest.approx(wg.dx_coupler) == 6.938129


def test_dx_mzi_none_intl(param) -> None:
    param['int_length'] = None
    wg = Waveguide(**param)
    with pytest.raises(TypeError):
        print(wg.dx_mzi)


def test_dx_mzi_none_arml(param) -> None:
    param['arm_length'] = None
    wg = Waveguide(**param)
    with pytest.raises(TypeError):
        print(wg.dx_mzi)


def test_dx_mzi(param) -> None:
    wg = Waveguide(**param)
    assert pytest.approx(wg.dx_mzi) == 10.876258


def test_dx_mzi_int_l(param) -> None:
    param['int_length'] = 2
    wg = Waveguide(**param)
    assert pytest.approx(wg.dx_mzi) == 14.876258


def test_dx_mzi_arml(param) -> None:
    param['arm_length'] = 3
    wg = Waveguide(**param)
    assert pytest.approx(wg.dx_mzi) == 12.876258


@pytest.mark.parametrize(
    'dy, r, exp',
    [
        (0.08, 0, pytest.raises(ValueError)),
        (0.08, 10, does_not_raise()),
        (0.08, None, pytest.raises(ValueError)),
        (None, 16, pytest.raises(ValueError)),
        (None, None, pytest.raises(ValueError)),
    ],
)
def test_get_sbend_param_error(dy, r, exp, param) -> None:
    wg = Waveguide(**param)
    with exp:
        wg.get_sbend_parameter(dy, r)


def test_get_sbend_param(param) -> None:
    dy = 0.08
    r = 30
    wg = Waveguide(**param)
    assert type(wg.get_sbend_parameter(dy, r)) == tuple
    assert pytest.approx(wg.get_sbend_parameter(dy, r)[0]) == 0.0516455
    assert pytest.approx(wg.get_sbend_parameter(dy, r)[1]) == 3.097354


@pytest.mark.parametrize('dy, r, exp', [(0.0, 15, 0.0), (0.127, 15, 2.757512)])
def test_get_sbend_length_nil_dy(dy, r, exp, param) -> None:
    wg = Waveguide(**param)
    assert pytest.approx(wg.get_sbend_parameter(dy, r)[1]) == exp


def test_repr(param) -> None:
    r = Waveguide(**param).__repr__()
    print()
    print(r)
    cname, _ = r.split('@')
    assert cname == 'Waveguide'


def test_circ_input_validation(param) -> None:
    a_i, a_f = 0, np.pi / 2

    param['radius'] = None
    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).circ(a_i, a_f)

    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).circ(a_i, a_f, radius=None)

    param['radius'] = 20
    wg = Waveguide(**param)
    wg.radius = None
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).circ(a_i, a_f)

    param['speed'] = None
    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).circ(a_i, a_f)

    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).circ(a_i, a_f, speed=None)

    param['speed'] = 15
    wg = Waveguide(**param)
    wg.speed = None
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).circ(a_i, a_f)


def test_circ_length(param) -> None:
    a_i, a_f = 0, np.pi / 2

    # DEFAULT VALUES FROM PARAM
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).circ(a_i, a_f)
    lc = np.abs(a_f - a_i) * wg.radius
    # add two points from the start method
    assert wg._x.size == int(np.ceil(lc * wg.cmd_rate_max / wg.speed)) + 2

    # CUSTOM RADIUS
    wg = Waveguide(**param)
    custom_r = 5
    wg.start([0, 0, 0]).circ(a_i, a_f, radius=custom_r)
    lc = np.abs(a_f - a_i) * custom_r
    assert wg._x.size == int(np.ceil(lc * wg.cmd_rate_max / wg.speed)) + 2

    # CUSTOM SPEED
    wg = Waveguide(**param)
    custom_f = 5
    wg.start([0, 0, 0]).circ(a_i, a_f, speed=custom_f)
    lc = np.abs(a_f - a_i) * wg.radius
    assert wg._x.size == int(np.ceil(lc * wg.cmd_rate_max / custom_f)) + 2


def test_circ_coordinates(param) -> None:
    a_i, a_f = 1.5 * np.pi, 0

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).circ(a_i, a_f)
    assert pytest.approx(wg._x[-1]) == wg.radius
    assert pytest.approx(wg._y[-1]) == wg.radius
    assert wg._z[-1] == wg._z[0]
    wg.end()

    a_i, a_f = 1.5 * np.pi, 1.75 * np.pi

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).circ(a_i, a_f)
    assert pytest.approx(wg._x[-1]) == wg.radius / np.sqrt(2)
    assert pytest.approx(wg._y[-1]) == wg.radius * (1 - 1 / np.sqrt(2))
    assert wg._z[-1] == wg._z[0]
    wg.end()


def test_circ_negative_radius(param) -> None:
    a_i, a_f = 1.5 * np.pi, 0

    wg = Waveguide(**param)
    wg.radius = -60
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).circ(a_i, a_f).end()


def test_arc_bend_dy(param):
    dy = 0.09
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_bend(dy).end()

    x, y, z, *_ = wg.points
    assert pytest.approx(np.max(z) - np.min(z)) == 0
    assert pytest.approx(np.max(y) - np.min(y)) == dy


def test_arc_bend_dy_default(param):
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_bend(wg.dy_bend).end()

    y = wg.y
    assert pytest.approx(np.max(y) - np.min(y)) == wg.dy_bend


def test_arc_bend_sign(param):
    dy = 0.03
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_bend(dy)
    y = wg.y
    assert y[-1] > y[0]
    wg.end()

    dy = -0.04
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_bend(dy)
    y = wg.y
    assert y[-1] < y[0]
    wg.end()


def test_arc_bend_none(param):
    dy = None
    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).arc_bend(dy).end()


def test_arc_bend_xlength(param):
    dy = 0.03

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_bend(dy)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == wg.get_sbend_parameter(dy, wg.radius)[1]
    wg.end()

    dy = 0.03
    r = 19
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_bend(dy=dy, radius=r)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == wg.get_sbend_parameter(dy, r)[1]
    wg.end()


def test_arc_bend_shutter(param):
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_bend(wg.dy_bend)
    *_, s = wg.points
    assert s[-1] == 1
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_bend(wg.dy_bend, shutter=0)
    *_, s = wg.points
    assert s[-1] == 0
    wg.end()


def test_arc_acc_len(param):
    dy = 0.055
    r = 32
    i_len = 1

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_coupler(dy=wg.dy_bend)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 2 * wg.get_sbend_parameter(wg.dy_bend, wg.radius)[1] + wg.int_length
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_coupler(dy=dy)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 2 * wg.get_sbend_parameter(dy, wg.radius)[1] + wg.int_length
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_coupler(dy=dy, radius=r)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 2 * wg.get_sbend_parameter(dy, r)[1] + wg.int_length
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_coupler(dy=dy, radius=r, int_length=i_len)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 2 * wg.get_sbend_parameter(dy, r)[1] + i_len
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_coupler(dy=wg.dy_bend, int_length=-i_len)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 2 * wg.get_sbend_parameter(wg.dy_bend, wg.radius)[1] + i_len
    wg.end()

    wg = Waveguide(**param)
    wg.int_length = None
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).arc_coupler(dy=wg.dy_bend, int_length=None).end()


def test_arc_mzi_len(param):
    dy = 0.065
    r = 24.6
    i_len = 5
    a_len = 8

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_mzi(dy=wg.dy_bend)
    x = wg.x
    assert (
        pytest.approx(x[-1] - x[0])
        == 4 * wg.get_sbend_parameter(wg.dy_bend, wg.radius)[1] + 2 * wg.int_length + wg.arm_length
    )
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_mzi(dy=dy)
    x = wg.x
    assert (
        pytest.approx(x[-1] - x[0]) == 4 * wg.get_sbend_parameter(dy, wg.radius)[1] + +2 * wg.int_length + wg.arm_length
    )
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_mzi(dy=dy, radius=r)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 4 * wg.get_sbend_parameter(dy, r)[1] + 2 * wg.int_length + wg.arm_length
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_mzi(dy=dy, radius=r, int_length=i_len)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 4 * wg.get_sbend_parameter(dy, r)[1] + 2 * i_len + wg.arm_length
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_mzi(dy=dy, radius=r, int_length=i_len, arm_length=a_len)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 4 * wg.get_sbend_parameter(dy, r)[1] + 2 * i_len + a_len
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).arc_mzi(dy=wg.dy_bend, int_length=-i_len, arm_length=-a_len)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 4 * wg.get_sbend_parameter(wg.dy_bend, wg.radius)[1] + 2 * i_len + a_len
    wg.end()

    wg = Waveguide(**param)
    wg.arm_length = None
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).arc_mzi(dy=wg.dy_bend, arm_length=None).end()


def test_sin_bridge_dy_default(param):
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bridge(dy=wg.dy_bend)
    y = wg.y
    assert pytest.approx(y[-1] - y[0]) == wg.dy_bend
    wg.end()


def test_sin_bridge_dy(param):
    dy = 0.2
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bridge(dy=dy)
    y = wg.y
    assert pytest.approx(y[-1] - y[0]) == dy
    wg.end()


def test_sin_bridge_dy_negative(param):
    dy = -0.5
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bridge(dy=dy)
    y = wg.y
    assert y[-1] - y[0] < 0
    assert pytest.approx(np.abs(y[-1] - y[0])) == np.abs(dy)
    wg.end()


def test_sin_bridge_dy_none(param):
    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).sin_bridge(dy=None).end()


def test_sin_bridge_dz_default(param):
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bridge(dy=wg.dy_bend)
    z = wg.z
    assert pytest.approx(np.max(z) - np.min(z)) == wg.dz_bridge
    wg.end()


def test_sin_bridge_dz_0(param):
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bridge(dy=wg.dy_bend, dz=0)
    z = wg.z
    assert pytest.approx(np.max(z) - np.min(z)) == 0.0
    wg.end()


def test_sin_bridge_dz(param):
    dz = 0.5
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bridge(dy=wg.dy_bend, dz=dz)
    z = wg.z
    assert pytest.approx(np.max(z) - np.min(z)) == dz
    wg.end()


def test_sin_bridge_dz_negative(param):
    dz = -0.89
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bridge(dy=wg.dy_bend, dz=dz)
    z = wg.z
    assert pytest.approx(np.max(z) - np.min(z)) == np.abs(dz)
    wg.end()


def test_sin_bridge_dz_none(param):
    wg = Waveguide(**param)
    wg.dz_bridge = None
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).sin_bridge(dy=wg.dy_bend, dz=None).end()


def test_sin_bridge_radius(param):
    r = 15
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bridge(dy=wg.dy_bend, dz=wg.dz_bridge, radius=r)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == wg.get_sbend_parameter(wg.dy_bend, r)[1]
    wg.end()


def test_sin_bridge_radius_negative(param):
    r = -10
    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).sin_bridge(dy=wg.dy_bend, dz=wg.dz_bridge, radius=r).end()


def test_sin_bridge_radius_none(param):
    wg = Waveguide(**param)
    wg.radius = None
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).sin_bridge(dy=wg.dy_bend, dz=wg.dz_bridge, radius=None).end()


def test_sin_bridge_speed(param):
    wg = Waveguide(**param)
    wg.speed = None
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).sin_bridge(dy=wg.dy_bend, dz=wg.dz_bridge, radius=None, speed=None).end()


def test_sin_bridge_length(param):
    r = 11
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bridge(dy=wg.dy_bend, dz=wg.dz_bridge, radius=r)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1] - x[0]) == wg.get_sbend_parameter(wg.dy_bend, np.abs(r))[1]
    assert pytest.approx(np.max(y) - np.min(y)) == wg.dy_bend
    assert pytest.approx(y[-1] - y[0]) == wg.dy_bend
    assert pytest.approx(np.max(z) - np.min(z)) == wg.dz_bridge
    wg.end()


def test_sin_bend_default(param):
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bend(dy=wg.dy_bend)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1] - x[0]) == wg.get_sbend_parameter(wg.dy_bend, np.abs(wg.radius))[1]
    assert pytest.approx(np.max(y) - np.min(y)) == wg.dy_bend
    assert pytest.approx(y[-1] - y[0]) == wg.dy_bend
    assert pytest.approx(np.max(z) - np.min(z)) == 0.0
    wg.end()


def test_sin_bend_values(param):
    r = 23
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bend(dy=wg.dy_bend, radius=r)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1] - x[0]) == wg.get_sbend_parameter(wg.dy_bend, np.abs(r))[1]
    assert pytest.approx(np.max(y) - np.min(y)) == wg.dy_bend
    assert pytest.approx(y[-1] - y[0]) == wg.dy_bend
    assert pytest.approx(np.max(z) - np.min(z)) == 0.0
    wg.end()

    r = 17
    dy = 0.9876
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_bend(dy=dy, radius=r)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1] - x[0]) == wg.get_sbend_parameter(dy, np.abs(r))[1]
    assert pytest.approx(np.max(y) - np.min(y)) == dy
    assert pytest.approx(y[-1] - y[0]) == dy
    assert pytest.approx(np.max(z) - np.min(z)) == 0.0
    wg.end()


def test_sin_comp_displacements(param):
    r = 15.3
    dy = 0.123
    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_comp(dy=dy, radius=r)
    x, y, z, *_ = wg.points
    assert pytest.approx(np.max(y) - np.min(y)) == dy
    assert pytest.approx(y[-1] - y[0]) == 0.0
    assert pytest.approx(np.max(z) - np.min(z)) == 0.0
    wg.end()


def test_sin_acc_len(param):
    dy = 0.415
    r = 12.04
    i_len = 1

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_coupler(dy=wg.dy_bend)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 2 * wg.get_sbend_parameter(wg.dy_bend, wg.radius)[1] + wg.int_length
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_coupler(dy=dy)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 2 * wg.get_sbend_parameter(dy, wg.radius)[1] + wg.int_length
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_coupler(dy=dy, radius=r)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 2 * wg.get_sbend_parameter(dy, r)[1] + wg.int_length
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_coupler(dy=dy, radius=r, int_length=i_len)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 2 * wg.get_sbend_parameter(dy, r)[1] + i_len
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_coupler(dy=wg.dy_bend, int_length=-i_len)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 2 * wg.get_sbend_parameter(wg.dy_bend, wg.radius)[1] + i_len
    wg.end()

    wg = Waveguide(**param)
    wg.int_length = None
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).sin_coupler(dy=wg.dy_bend, int_length=None).end()


def test_sin_mzi_len(param):
    dy = 0.3335
    r = 28.12
    i_len = 5
    a_len = 8

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_mzi(dy=wg.dy_bend)
    x = wg.x
    assert (
        pytest.approx(x[-1] - x[0])
        == 4 * wg.get_sbend_parameter(wg.dy_bend, wg.radius)[1] + 2 * wg.int_length + wg.arm_length
    )
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_mzi(dy=dy)
    x = wg.x
    assert (
        pytest.approx(x[-1] - x[0]) == 4 * wg.get_sbend_parameter(dy, wg.radius)[1] + 2 * wg.int_length + wg.arm_length
    )
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_mzi(dy=dy, radius=r)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 4 * wg.get_sbend_parameter(dy, r)[1] + 2 * wg.int_length + wg.arm_length
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_mzi(dy=dy, radius=r, int_length=i_len)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 4 * wg.get_sbend_parameter(dy, r)[1] + 2 * i_len + wg.arm_length
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_mzi(dy=dy, radius=r, int_length=i_len, arm_length=a_len)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 4 * wg.get_sbend_parameter(dy, r)[1] + 2 * i_len + a_len
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).sin_mzi(dy=wg.dy_bend, int_length=-i_len, arm_length=-a_len)
    x = wg.x
    assert pytest.approx(x[-1] - x[0]) == 4 * wg.get_sbend_parameter(wg.dy_bend, wg.radius)[1] + 2 * i_len + a_len
    wg.end()

    wg = Waveguide(**param)
    wg.arm_length = None
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).sin_mzi(dy=wg.dy_bend, arm_length=None).end()


def test_spline_dy_default(param):
    dx = 5
    dz = 0.01

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline(disp_x=dx, dy=wg.dy_bend, dz=dz)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1] - x[0]) == dx
    assert pytest.approx(y[-1] - y[0]) == wg.dy_bend
    assert pytest.approx(np.max(z) - np.min(z)) == dz
    wg.end()


def test_spline_dy_custom(param):
    dx = 3.12
    dy = 0.08
    dz = 0.15

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline(disp_x=dx, dy=dy, dz=dz)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1] - x[0]) == dx
    assert pytest.approx(y[-1] - y[0]) == dy
    assert pytest.approx(np.max(z) - np.min(z)) == dz
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline(disp_x=dx, dy=-dy, dz=dz)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1] - x[0]) == dx
    assert pytest.approx(y[-1] - y[0]) == -dy
    assert pytest.approx(np.max(z) - np.min(z)) == dz
    wg.end()


def test_spline_dy_none(param):
    dx = 5
    dz = 0.01

    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).spline(disp_x=dx, dy=None, dz=dz).end()


def test_spline_dz_default(param):
    dx = 5
    dy = 0.01

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline(disp_x=dx, dy=dy, dz=wg.dz_bridge)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1] - x[0]) == dx
    assert pytest.approx(y[-1] - y[0]) == dy
    assert pytest.approx(z[-1] - z[0]) == wg.dz_bridge
    wg.end()


def test_spline_dz_custom(param):
    dx = 3.12
    dy = 1.85
    dz = 1.2

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline(disp_x=dx, dy=dy, dz=dz)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1] - x[0]) == dx
    assert pytest.approx(y[-1] - y[0]) == dy
    assert pytest.approx(z[-1] - z[0]) == dz
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline(disp_x=dx, dy=dy, dz=-dz)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1] - x[0]) == dx
    assert pytest.approx(y[-1] - y[0]) == dy
    assert pytest.approx(z[-1] - z[0]) == -dz
    wg.end()


def test_spline_dz_none(param):
    dx = 7
    dy = 0.01

    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).spline(disp_x=dx, dy=dy, dz=None).end()


def test_spline_init_pos_default(param):
    dx = 3.12
    dy = 1.85
    dz = 1.2
    init_p = [-1, 5, -0.21]

    wg = Waveguide(**param)
    wg.start(init_p).spline(disp_x=dx, dy=dy, dz=dz)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1]) == dx + init_p[0]
    assert pytest.approx(y[-1]) == dy + init_p[1]
    assert pytest.approx(z[-1]) == dz + init_p[2]
    wg.end()


def test_spline_init_pos_custom(param):
    dx = 3.12
    dy = 1.85
    dz = 1.2
    i_pos = np.array([5.8, 9.2, 3.57])

    wg = Waveguide(**param)
    wg.x_init = 1.0
    wg.y_init = 2.0
    wg.z_init = 3.0
    wg.start(i_pos).spline(disp_x=dx, dy=dy, dz=dz)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1]) == dx + i_pos[0]
    assert pytest.approx(y[-1]) == dy + i_pos[1]
    assert pytest.approx(z[-1]) == dz + i_pos[2]
    wg.end()


def test_spline_init_none(param):
    # if wg.x_init, wg.y_init, wg.z_init are None and init_point is None attach the spline to last point

    x0, y0, z0 = (5, 6, 7)
    dx, dy, dz = (1.2, 2.3, 3.4)

    wg = Waveguide(**param)
    wg.x_init = None
    wg.y_init = None
    wg.z_init = None
    wg.start([x0, y0, z0]).spline(disp_x=dx, dy=dy, dz=dz)
    x, y, z, *_ = wg.points
    assert pytest.approx(x[-1]) == dx + x0
    assert pytest.approx(y[-1]) == dy + y0
    assert pytest.approx(z[-1]) == dz + z0
    wg.end()


def test_spline_radius_default(param):
    dy, dz = (0.3, 0.69)

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline(disp_x=None, dy=dy, dz=dz)
    x = wg.x
    assert pytest.approx(x[-1]) == wg.get_sbend_parameter(np.sqrt(dy**2 + dz**2), wg.radius)[1]
    wg.end()


def test_spline_radius_custom(param):
    dy, dz = (0.3, 0.69)
    r = 90

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline(disp_x=None, dy=dy, dz=dz, radius=r)
    x = wg.x
    assert pytest.approx(x[-1]) == wg.get_sbend_parameter(np.sqrt(dy**2 + dz**2), r)[1]
    wg.end()


def test_spline_radius_none(param):
    dy, dz = (0.3, 0.69)
    r = None

    wg = Waveguide(**param)
    wg.radius = None
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).spline(disp_x=None, dy=dy, dz=dz, radius=r).end()


def test_spline_speed_none(param):
    dx, dy, dz = (0.1, 0.23, 0.456)
    wg = Waveguide(**param)
    wg.speed = None
    with pytest.raises(ValueError):
        wg.start([0, 0, 0]).spline(disp_x=dx, dy=dy, dz=dz, speed=None).end()


@pytest.mark.parametrize(
    'ddy', [((0.0, 0.0), (0.0, 0.0)), ((1.0, 0.0), (1.0, 1.0)), ((-2.0, 0.5), (0.5, 0.6)), ((0.1, 0.1), (0.0, 0.23))]
)
def test_spline_y_derivative(param, ddy):
    dx, dy, dz = (0.1, 0.23, 0.456)
    dz_der = ((0.0, 0.0), (0.0, 0.0))

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline(dy=dy, dz=dz, y_derivatives=ddy, z_derivatives=dz_der)

    # Extract the x and y coordinates as separate arrays
    x, y, z = wg.path3d
    yp = np.gradient(y, x)
    ypp = 2 * np.gradient(yp, x)

    assert pytest.approx(yp[0], abs=1e-1) == ddy[0][0]
    assert pytest.approx(yp[-2], abs=1e-1) == ddy[-1][0]
    assert pytest.approx(ypp[0], abs=1e-1) == ddy[0][1]
    assert pytest.approx(ypp[-1], abs=1e-1) == ddy[-1][1]


@pytest.mark.parametrize(
    'ddz', [((0.0, 0.0), (0.0, 0.0)), ((1.0, 0.0), (1.0, 1.0)), ((-2.0, 0.5), (0.5, 0.6)), ((0.1, 0.1), (0.0, 0.23))]
)
def test_spline_z_derivative(param, ddz):
    dx, dy, dz = (0.1, 0.23, 0.456)
    dy_der = ((0.0, 0.0), (0.0, 0.0))

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline(dy=dy, dz=dz, y_derivatives=dy_der, z_derivatives=ddz)

    # Extract the x and y coordinates as separate arrays
    x, y, z = wg.path3d
    zp = np.gradient(z, x)
    zpp = 2 * np.gradient(zp, x)

    assert pytest.approx(zp[0], abs=1e-1) == ddz[0][0]
    assert pytest.approx(zp[-2], abs=1e-1) == ddz[-1][0]
    assert pytest.approx(zpp[0], abs=1e-1) == ddz[0][1]
    assert pytest.approx(zpp[-1], abs=1e-1) == ddz[-1][1]


@pytest.mark.parametrize('r_input', [5, 10, 15, 20, 25, 30, 35, 40, 50, 60])
def test_curvature_radius(param, r_input) -> None:
    # mean curvature radius is within 5% of the original radius
    r = r_input
    x = 0.05
    wg = Waveguide(**param)
    wg.start().circ(0, 3 * np.pi / 2, radius=r)

    assert np.mean(wg.curvature_radius) <= (1 + x) * r
    assert np.mean(wg.curvature_radius) >= (1 - x) * r


def test_curvature_radius_default(param) -> None:
    # mean curvature radius is within 5% of the default radius
    x = 0.05
    wg = Waveguide(**param)
    wg.start().circ(0, 3 * np.pi / 2)

    assert np.mean(wg.curvature_radius) <= (1 + x) * wg.radius
    assert np.mean(wg.curvature_radius) >= (1 - x) * wg.radius


def test_cmd_rate(param) -> None:
    wg = Waveguide(**param)
    wg.start().linear([1, 2, 3], mode='abs').sin_mzi(wg.dy_bend).linear([4, 5, 6]).end()

    assert np.mean(wg.cmd_rate) <= wg.cmd_rate_max


def test_spline_bridge_error(param) -> None:
    wg = Waveguide(**param)
    with pytest.raises(ValueError):
        wg.start().spline_bridge(disp_x=None, dy=None, dz=None).end()

    with pytest.raises(ValueError):
        wg.start().spline_bridge(disp_x=None, dy=0.05, dz=None).end()

    with pytest.raises(ValueError):
        wg.start().spline_bridge(disp_x=None, dy=None, dz=0.006).end()


def test_spline_bridge_speed(param) -> None:
    dy, dz, f_custom = (0.06, 0.006, 99)

    wg = Waveguide(**param)
    wg.start().spline_bridge(disp_x=None, dy=dy, dz=dz)
    assert wg._f[-1] == wg.speed
    wg.end()

    wg = Waveguide(**param)
    wg.start().spline_bridge(disp_x=None, dy=dy, dz=dz, speed=f_custom)
    assert wg._f[-1] == f_custom
    wg.end()


def test_spline_bridge_dx(param) -> None:
    dx, dy, dz = (10, 0.06, 0.006)

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline_bridge(disp_x=None, dy=dy, dz=dz)
    assert pytest.approx(wg.x[-1]) == 2 * wg.get_sbend_parameter(dy=np.sqrt(dy**2 + dz**2), radius=wg.radius)[-1]
    wg.end()

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline_bridge(disp_x=dx, dy=dy, dz=dz)
    assert pytest.approx(wg.x[-1]) == 2 * dx
    wg.end()


def test_spline_bridge_dy_dz(param) -> None:
    dx, dy, dz = (15, 0.789, 0.123)

    wg = Waveguide(**param)
    wg.start([0, 0, 0]).spline_bridge(disp_x=dx, dy=dy, dz=dz)
    assert pytest.approx(wg.y[-1]) == dy
    assert pytest.approx(wg.z[-1] - wg.z[0], abs=1e-8) == 0.0
    assert pytest.approx(np.max(wg.z) - np.min(wg.z)) == dz
    wg.end()


def test_spline_bridge_derivatives(param) -> None:
    dx, dy, dz = (19.45, 12.38, 3.56)
    wg = Waveguide(**param)

    wg.start([0, 0, 0.5]).spline_bridge(disp_x=dx, dy=dy, dz=dz)
    x, y, z = wg.path3d
    assert pytest.approx((y[1] - y[0]) / (x[1] - x[0]), abs=1e-2) == 0.0
    assert pytest.approx((y[-2] - y[-1]) / (x[-2] - x[-1]), abs=1e-2) == 0.0
    assert pytest.approx((z[1] - z[0]) / (x[1] - x[0]), abs=1e-2) == 0.0
    assert pytest.approx((z[-2] - z[-1]) / (x[-2] - x[-1]), abs=1e-2) == 0.0


def test_nasu_default_values() -> None:
    ng = NasuWaveguide()
    assert ng.scan == int(1)
    assert ng.speed == float(1.0)
    assert ng.x_init == float(-2.0)
    assert ng.y_init == float(0.0)
    assert ng.z_init == float(0.035)
    assert ng.lsafe == float(2.0)
    assert ng.speed_closed == float(5.0)
    assert ng.speed_pos == float(0.5)
    assert ng.cmd_rate_max == int(1200)
    assert ng.acc_max == int(500)
    assert ng.samplesize == (100, 50)
    assert ng.depth == float(0.035)
    assert ng.radius == float(15)
    assert ng.pitch == float(0.080)
    assert ng.pitch_fa == float(0.127)
    assert ng.int_dist is None
    assert ng.int_length == float(0.0)
    assert ng.arm_length == float(0.0)
    # assert ng.ltrench == float(1.0)
    assert ng.dz_bridge == float(0.007)
    assert ng.adj_scan_shift == (0, 0.0004, 0)
    assert ng.adj_scan == int(5)


def test_nasu_values(param) -> None:
    ng = NasuWaveguide(adj_scan_shift=(0.1, 0.2, 0.003), adj_scan=3, **param)
    assert ng.scan == int(6)
    assert ng.speed == float(20.0)
    assert ng.x_init == float(-2.0)
    assert ng.y_init == float(1.5)
    assert ng.z_init == float(0.050)
    assert ng.lsafe == float(2.0)
    assert ng.speed_closed == float(75)
    assert ng.speed_pos == float(0.5)
    assert ng.cmd_rate_max == int(1200)
    assert ng.acc_max == int(500)
    assert ng.samplesize == (100, 15)
    assert ng.depth == float(0.035)
    assert ng.radius == float(25)
    assert ng.pitch == float(0.127)
    assert ng.pitch_fa == float(0.127)
    assert ng.int_dist == float(0.005)
    assert ng.int_length == float(0.0)
    assert ng.arm_length == float(1.0)
    # assert ng.ltrench == float(1.5)
    assert ng.dz_bridge == float(0.006)
    assert ng.adj_scan_shift == (0.1, 0.2, 0.003)
    assert ng.adj_scan == int(3)


@pytest.mark.parametrize(
    'a_scan, exp',
    [
        (3, does_not_raise()),
        (3.33, pytest.raises(ValueError)),
        (0.01, pytest.raises(ValueError)),
        (5, does_not_raise()),
        (2, does_not_raise()),
    ],
)
def test_nasu_raise(a_scan, exp, param) -> None:
    with exp:
        NasuWaveguide(adj_scan=a_scan, **param)


@pytest.mark.parametrize(
    'a_scan, exp',
    [
        (3, [0, 1, -1]),
        (5, [0, 1, -1, 2, -2]),
        (17, [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8]),
        (1, [0]),
        (4, [0.5, -0.5, 1.5, -1.5]),
        (8, [0.5, -0.5, 1.5, -1.5, 2.5, -2.5, 3.5, -3.5]),
    ],
)
def test_nasu_adjscans(param, a_scan, exp) -> None:
    ng = NasuWaveguide(adj_scan=a_scan)
    assert ng.adj_scan_order == exp


def test_coupler_pitch(param) -> None:
    mode1, mode2 = coupler(param)
    assert mode2.y[-1] == pytest.approx(mode1.y[-1] + param['pitch'])


def test_coupler_wg_type(param) -> None:
    mode1, mode2 = coupler(param, nasu=False)
    assert type(mode1) == type(mode2)
    assert type(mode1) == Waveguide
    del mode1, mode2

    mode1, mode2 = coupler(param, nasu=True)
    assert type(mode1) == type(mode2)
    assert type(mode1) == NasuWaveguide


@pytest.mark.parametrize('d_input', [0.000, 0.001, 0.002, 0.003, 0.005, 0.007, 0.009, 0.0011, 0.0015, 0.0025])
def test_coupler_d_int(d_input) -> None:
    p = {
        'scan': 6,
        'speed': 20.0,
        'samplesize': (100, 15),
        'depth': 0.035,
        'radius': 25,
        'pitch': 0.127,
        'int_dist': d_input,
        'int_length': 0.0,
        'arm_length': 1.0,
    }

    mode1, mode2 = coupler(p)

    # test difference between min/max of mode2 and mode1 (respectively) is int_dist
    assert pytest.approx(np.min(mode2.y) - np.max(mode1.y), abs=1e-6) == d_input
    # test the point of min distance is at the same x value
    assert pytest.approx(mode2.x[np.where(mode2.y == np.min(mode2.y))]) == mode1.x[np.where(mode1.y == np.max(mode1.y))]
