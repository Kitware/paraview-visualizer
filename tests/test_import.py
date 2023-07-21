def test_import():
    try:
        from pv_visualizer.app import main  # noqa: F401
    except ModuleNotFoundError:
        # missing paraview
        pass
