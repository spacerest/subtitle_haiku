# subtitle zappai

looks in .srt english subtitle files for groups of subtitles that follow a 5 - 7 - 5 syllable pattern. 

it can be used by running it with 

```python find_zappai.py```

in a directory containing the .srt files to search.

sometimes I post some images, gifs, or movies to [@subtitle_haiku](https://twitter.com/subtitle_haiku)

# other notes

[how to convert a mov to a gif](https://superuser.com/a/436109/745836)

```ffmpeg -ss 00:00:00.000 -i input.mov -pix_fmt rgb24 -r 10 -t 00:00:10.000 output.gif```

(optional optimization)
```convert -layers Optimize so_thats_orion.gif output_optimized.gif```
