import cProfile
import pstats


class DebugHandler:

    def __init__(self, gh):
        self.gh = gh
        self.ready_to_calculate = False
        self.previous_time = None
        self.frame_count = None

    @staticmethod
    def debug_lag(func):
        if func is not None:
            profiler = cProfile.Profile()
            profiler.enable()
            func()
            profiler.disable()
            stats = pstats.Stats(profiler).sort_stats('time')
            stats.print_stats(10)

    def debug_fps(self):

        if not self.ready_to_calculate:
            self.previous_time = self.gh.pygame.time.get_ticks()
            self.frame_count = 0
            self.ready_to_calculate = True

        else:
            current_time = self.gh.pygame.time.get_ticks()
            self.frame_count += 1
            elapsed_time = current_time - self.previous_time
            if elapsed_time >= 1000:
                fps = self.frame_count / (elapsed_time / 1000.0)
                print(f"FPS: {fps:.2f}")
                self.previous_time = current_time
                self.frame_count = 0
