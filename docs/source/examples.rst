========
Examples
========

There are several examples distributed with Pycha. You can find them in the
``examples`` directory. Let's analyze some of them.

Bar charts
----------

One of the most common used charts are bar charts. In the
``examples/barchart.py`` programm there are examples of vertical and
horizontal bar charts::

  import sys
  import cairo
  import pycha.bar

  from lines import lines


  def barChart(output, chartFactory):
      surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 400)

      dataSet = (
          ('lines', [(i, l[1]) for i, l in enumerate(lines)]),
          )

      options = {
          'axis': {
              'x': {
                  'ticks': [dict(v=i, label=l[0]) for i, l in enumerate(lines)],
                  'label': 'Files',
                  'rotate': 25,
              },
              'y': {
                  'tickCount': 4,
                  'rotate': 25,
                  'label': 'Lines'
              }
          },
          'background': {
              'chartColor': '#ffeeff',
              'baseColor': '#ffffff',
              'lineColor': '#444444'
          },
          'colorScheme': {
              'name': 'gradient',
              'args': {
                  'initialColor': 'red',
              },
          },
          'legend': {
              'hide': True,
          },
          'padding': {
              'left': 0,
              'bottom': 0,
          },
          'title': 'Sample Chart'
      }
      chart = chartFactory(surface, options)

      chart.addDataset(dataSet)
      chart.render()

      surface.write_to_png(output)

  if __name__ == '__main__':
      if len(sys.argv) > 1:
          output = sys.argv[1]
      else:
          output = 'barchart.png'
      barChart('v' + output, pycha.bar.VerticalBarChart)
      barChart('h' + output, pycha.bar.HorizontalBarChart)

There are several things we can note in this source code listing:

* The ``barChart`` function will create a bar chart and save it to a png file
* The information shown in the chart is takes from the ``lines.py`` module,
  which, basically is a python module with a dataset composed of the
  number of lines that some Pycha modules have.
* Most of the code is about setting the options dictionary. We will see
  more about these options in the reference chapter but they should be
  pretty intuitive.

Let's see the output of running this programm.

.. figure:: _static/vbarchart.png
   :alt: Vertical Bar Chart

   Vertical Bar Chart

   Example of vertical bar chart found in the Pycha examples directory


.. figure:: _static/hbarchart.png
   :alt: Horizontal Bar Chart

   Horizontal Bar Chart

   Example of horizontal bar chart found in the Pycha examples directory
