# Credits

## Photos

Photographs in `frontend/src/assets/` come from [Unsplash](https://unsplash.com) under the
[Unsplash License](https://unsplash.com/license) (free to use, no attribution required — credited
here anyway). They are resized and re-encoded to WebP at build-friendly sizes.

| File | Photo | Photographer |
| --- | --- | --- |
| `hero-squat.webp` | [A man squatting down next to a barbell in a gym](https://unsplash.com/photos/8LWo8v0mKik) | Redd Francisco |
| `hero-rack.webp` | [Barbell on rack](https://unsplash.com/photos/gzeTjGu3b_k) | Jelmer Assink |

## Exercise drawings

The exercise drawings in `frontend/public/exercise-art/` come from
[Workout Guide](https://github.com/bryllim/workout-guide) by [Bryl Lim](https://bryllim.com), whose
original poses come from [Everkinetic](https://github.com/everkinetic/data). They are licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

Changes: the middle frame of each drawing is trimmed to the figure, scaled down and re-encoded as
WebP by `frontend/scripts/build_exercise_art.py`, pinned to upstream commit `aac5992`. The resulting
thumbnails are shared under the same CC BY-SA 4.0 licence. Which drawing each catalog exercise uses
is listed in `frontend/src/features/workout/exercise-art.json`; some exercises reuse the drawing of a
close variant.
