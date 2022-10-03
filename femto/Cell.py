import os
import time

import numpy as np
import plotly.graph_objects as go
from femto import Marker, PGMCompiler, PGMTrench, Trench, TrenchColumn, Waveguide
from femto.helpers import listcast, nest_level
from shapely.affinity import rotate, translate
from shapely.geometry import Point


class Device(PGMCompiler):
    def __init__(self, param):
        super(Device, self).__init__(param)
        self._param = param
        self.waveguides = []
        self.markers = []
        self.trench_cols = []
        self.trenches = []
        self.fig = None

    def append(self, obj):
        if isinstance(obj, Cell):
            self.markers.extend(obj.markers)
            self.waveguides.extend(obj.waveguides)
            self.trenches.extend(obj.trenches)
        elif isinstance(obj, Marker):
            self.markers.append(obj)
        elif isinstance(obj, Waveguide) or (isinstance(obj, list) and all(isinstance(x, Waveguide) for x in obj)):
            self.waveguides.append(obj)
        elif isinstance(obj, Trench):
            self.trenches.append(obj)
        elif isinstance(obj, TrenchColumn):
            for trc in obj:
                self.append(trc)
            self.trench_cols.append(obj)
        else:
            raise TypeError(f'The object must be a Waveguide, Marker or Trench object. {type(obj)} was given.')

    def plot2d(self, shutter_close: bool = True, aspect: str = 'auto', wg_style=None, sc_style=None, mk_style=None,
               tc_style=None, pc_style=None, gold_layer: bool = False, show: bool = True):
        if wg_style is None:
            wg_style = dict()
        if sc_style is None:
            sc_style = dict()
        if mk_style is None:
            mk_style = dict()
        if tc_style is None:
            tc_style = dict()
        if pc_style is None:
            pc_style = dict()
        default_wgargs = {'dash': 'solid', 'color': '#0000ff', 'width': 1.5, }
        wgargs = {**default_wgargs, **wg_style}
        default_scargs = {'dash': 'dot', 'color': '#0000ff', 'width': 0.5}
        scargs = {**default_scargs, **sc_style}
        default_mkargs = {'dash': 'solid', 'color': '#000000', 'width': 2.0}
        mkargs = {**default_mkargs, **mk_style}
        default_tcargs = {'fillcolor': '#7E7E7E', 'mode': 'none', 'hoverinfo': 'none'}
        tcargs = {**default_tcargs, **tc_style}
        if gold_layer:
            default_pcargs = {'fillcolor': '#FFD700', 'line_color': '#000000', 'line_width': 2, 'layer': 'below', }
        else:
            default_pcargs = {'fillcolor': '#D0FAF9', 'line_color': '#000000', 'line_width': 2, 'layer': 'below', }
        pcargs = {**default_pcargs, **pc_style}

        self.fig = go.Figure()

        for bunch in self.waveguides:
            for wg in listcast(bunch):
                p = np.array(self.transform_points(wg.points)).T
                xo, yo, _ = self._shutter_mask(p, shutter=1)
                self.fig.add_trace(go.Scattergl(x=xo, y=yo,
                                                mode='lines',
                                                line=wgargs,
                                                showlegend=False,
                                                hovertemplate='(%{x:.4f}, %{y:.4f})<extra>WG</extra>'))
                if shutter_close:
                    xc, yc, _ = self._shutter_mask(p, shutter=0)
                    self.fig.add_trace(go.Scattergl(x=xc, y=yc,
                                                    mode='lines',
                                                    line=scargs,
                                                    hoverinfo='none',
                                                    showlegend=False, ))
        for mk in self.markers:
            p = np.array(self.transform_points(mk.points)).T
            xo, yo, _ = self._shutter_mask(p, shutter=1)
            self.fig.add_trace(go.Scattergl(x=xo, y=yo,
                                            mode='lines',
                                            line=mkargs,
                                            showlegend=False,
                                            hovertemplate='(%{x:.4f}, %{y:.4f})<extra>MK</extra>'))
        for tr in self.trenches:
            shape = translate(tr.block, xoff=-self.new_origin[0], yoff=-self.new_origin[1])
            shape = rotate(shape, angle=self.angle, use_radians=True, origin=Point(0, 0))
            xt, yt = np.asarray(shape.exterior.coords.xy)
            self.fig.add_trace(go.Scattergl(x=xt, y=yt,
                                            fill='toself',
                                            **default_tcargs,
                                            showlegend=False,
                                            hovertemplate='(%{x:.4f}, %{y:.4f})<extra>TR</extra>'))

        # GLASS
        self.fig.add_shape(type='rect', x0=0 - self.new_origin[0], y0=0 - self.new_origin[1],
                           x1=self.xsample - self.new_origin[0], y1=self.ysample - self.new_origin[1],
                           **default_pcargs)

        # ORIGIN
        self.fig.add_trace(go.Scattergl(x=[0], y=[0],
                                        marker=dict(color='red', size=12),
                                        hoverinfo='none',
                                        showlegend=False, ))

        # TODO: axis = 'equal' feature
        # if isinstance(aspect, str) and aspect.lower() not in ['auto', 'equal']:
        #     raise ValueError(f'aspect must be either `auto` or `equal`. Given {aspect.lower()}.')
        # self.ax.set_aspect(aspect)

        self.fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title='x [mm]',
                           showgrid=False,
                           zeroline=False, ),
                yaxis=dict(title='y [mm]',
                           showgrid=False,
                           zeroline=False, ),
                annotations=[dict(x=0, y=0,
                                  text='(0,0)',
                                  showarrow=False,
                                  xanchor="left",
                                  xshift=-25,
                                  yshift=-20,
                                  font=dict(color='red'))]
        )

        # SHOW
        if show:
            self.fig.show()
        return self.fig

    def plot3d(self, shutter_close: bool = True, wg_style=None, sc_style=None, mk_style=None, show: bool = True):
        if wg_style is None:
            wg_style = dict()
        if sc_style is None:
            sc_style = dict()
        if mk_style is None:
            mk_style = dict()
        default_wgargs = {'dash': 'solid', 'color': '#0000ff', 'width': 1.5, }
        wgargs = {**default_wgargs, **wg_style}
        default_scargs = {'dash': 'dot', 'color': '#0000ff', 'width': 0.5}
        scargs = {**default_scargs, **sc_style}
        default_mkargs = {'dash': 'solid', 'color': '#000000', 'width': 2.0}
        mkargs = {**default_mkargs, **mk_style}

        self.fig = go.Figure()

        for bunch in self.waveguides:
            for wg in listcast(bunch):
                p = np.array(self.transform_points(wg.points)).T
                xo, yo, zo = self._shutter_mask(p, shutter=1)
                self.fig.add_trace(go.Scatter3d(x=xo, y=yo, z=zo,
                                                mode='lines',
                                                line=wgargs,
                                                showlegend=False,
                                                hovertemplate='(%{x:.4f}, %{y:.4f}), %{z:.4f})<extra>WG</extra>'))
                if shutter_close:
                    xc, yc, zc = self._shutter_mask(p, shutter=0)
                    self.fig.add_trace(go.Scatter3d(x=xc, y=yc, z=zc,
                                                    mode='lines',
                                                    line=scargs,
                                                    hoverinfo='none',
                                                    showlegend=False, ))

        for mk in self.markers:
            p = np.array(self.transform_points(mk.points)).T
            xo, yo, zo = self._shutter_mask(p, shutter=1)
            self.fig.add_trace(go.Scatter3d(x=xo, y=yo, z=zo,
                                            mode='lines',
                                            line=mkargs,
                                            showlegend=False,
                                            hovertemplate='<extra>MK</extra>'))

        # ORIGIN
        self.fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0],
                                        marker=dict(color='red', size=12),
                                        hoverinfo='none',
                                        showlegend=False, ))

        self.fig.update_layout(
                scene=dict(
                        bgcolor='rgba(0,0,0,0)',
                        aspectratio=dict(
                                x=2,
                                y=1,
                                z=0.25,
                        ),
                        xaxis=dict(title='x [mm]',
                                   showgrid=False,
                                   zeroline=False, ),
                        yaxis=dict(title='y [mm]',
                                   showgrid=False,
                                   zeroline=False, ),
                        zaxis=dict(title='z [mm]',
                                   showgrid=False,
                                   zeroline=False, ),
                        annotations=[dict(x=0, y=0, z=0,
                                          text='(0,0,0)',
                                          showarrow=False,
                                          xanchor="left",
                                          xshift=10,
                                          font=dict(color='red'))]
                )
        )

        # SHOW
        if show:
            self.fig.show()
        return self.fig

    def save(self, filename='device_scheme.html'):
        extension = os.path.splitext(filename)[1][1:].strip()

        if extension == '': filename += '.html'
        if extension.lower() in ['html', '']:
            self.fig.write_html(filename)
        else:
            self.fig.write_image(filename, width=1980, height=1080, scale=2, engine='kaleido')

    @staticmethod
    def _shutter_mask(points, shutter: int = 1):
        if shutter not in [0, 1]:
            raise ValueError(f'Shutter must be either OPEN (1) or CLOSE (0). Given {shutter}.')
        x, y, z, _, s = points.T
        ym = np.where(s == shutter, y, np.nan)
        zm = np.where(s == shutter, z, np.nan)
        return x, ym, zm


class Cell(Device):
    def __init__(self, param):
        super(Cell, self).__init__(param)

    def pgm(self, verbose: bool = True, waveguide: bool = True, marker: bool = True, trench: bool = True):
        if waveguide:
            self._wg_pgm(verbose=verbose)
        if marker:
            self._mk_pgm(verbose=verbose)
        if trench:
            self._tc_pgm(verbose=verbose)

    # Private interface
    def _wg_pgm(self, verbose: bool = True):

        if nest_level(self.waveguides) > 2:
            raise ValueError(f'The waveguide list has too many nested levels ({nest_level(self.waveguides)}. '
                             'The maximum value is 2.')
        if not self.waveguides:
            return

        _wg_fab_time = 0.0
        self.filename = self.filename.split('.')[0]
        wg_filename = self.filename.split('.')[0] + '_WG.pgm'

        self.header()
        self.dwell(1.0)

        for bunch in self.waveguides:
            with self.repeat(listcast(bunch)[0].scan):
                for wg in listcast(bunch):
                    _wg_fab_time += wg.wtime
                    self.write(wg.points)
        self.go_init()

        with open(wg_filename, 'w') as f:
            f.write(''.join(self._instructions))
        if verbose:
            print('G-code compilation completed.')
            print('Estimated fabrication time of the optical device: ',
                  time.strftime('%H:%M:%S', time.gmtime(_wg_fab_time + self._total_dwell_time)))
        self._instructions.clear()
        self._total_dwell_time = 0.0

    def _mk_pgm(self, verbose: bool = True):

        if nest_level(self.markers) > 1:
            raise ValueError(f'The markers list has too many nested levels ({nest_level(self.markers)}. '
                             'The maximum value is 1.')
        if not self.markers:
            return

        _mk_fab_time = 0.0
        self.filename = self.filename.split('.')[0]
        mk_filename = self.filename.split('.')[0] + '_MARKERS.pgm'

        self.header()
        self.dwell(1.0)

        for bunch in self.markers:
            with self.repeat(listcast(bunch)[0].scan):
                for mk in listcast(bunch):
                    _mk_fab_time += mk.wtime
                    self.write(mk.points)
        self.homing()

        with open(mk_filename, 'w') as f:
            f.write(''.join(self._instructions))
        if verbose:
            print('G-code compilation completed.')
            print('Estimated fabrication time of the markers: ',
                  time.strftime('%H:%M:%S', time.gmtime(_mk_fab_time + self._total_dwell_time)))
        self._instructions.clear()
        self._total_dwell_time = 0.0

    def _tc_pgm(self, verbose: bool = True):
        t_writer = PGMTrench(self._param, self.trench_cols)
        t_writer.write()

        if verbose:
            _tc_fab_time = 0.0
            for col in self.trench_cols:
                _tc_fab_time += col.wtime

            print('G-code compilation completed.')
            print('Estimated fabrication time of the isolation trenches: ',
                  time.strftime('%H:%M:%S', time.gmtime(_tc_fab_time + t_writer._total_dwell_time)))
        del t_writer

def _example():
    from femto.helpers import dotdict

    PARAMETERS_GC = dotdict(
            filename='testMarker.pgm',
            lab='CAPABLE',
            new_origin=(0.5, 0.5),
            samplesize=(25, 1),
            angle=0.0,
    )

    PARAMETERS_WG = dotdict(
            scan=6,
            speed=20,
            radius=15,
            pitch=0.080,
            int_dist=0.007,
            lsafe=5,
    )

    increment = [PARAMETERS_WG.lsafe, 0, 0]
    c = Cell(PARAMETERS_GC)

    # Calculations
    mzi = [Waveguide(PARAMETERS_WG) for _ in range(2)]
    y0 = PARAMETERS_GC.samplesize[1] / 2
    for index, wg in enumerate(mzi):
        [xi, yi, zi] = [-2, -wg.pitch / 2 + index * wg.pitch + y0, 0.035]

        wg.start([xi, yi, zi]) \
            .linear(increment) \
            .sin_mzi((-1) ** index * wg.dy_bend) \
            .linear([5, 0, 0]) \
            .sin_mzi((-1) ** index * wg.dy_bend) \
            .linear([27, yi, zi], mode='ABS')
        wg.end()
        c.append(wg)

    c.plot2d()
    # c.save('circuit_scheme.pdf')
    # c.pgm()


if __name__ == '__main__':
    _example()
