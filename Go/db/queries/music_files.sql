-- name: UpdateMusicFilesSetAllFileNotExists :exec
update arabot.music_files set file_exists = 0;

-- name: MergeMusicFiles :exec
INSERT INTO arabot.music_files (
  first_char_performer_display_name,
  performer_display_name,
  album_display_name,
  song_display_name,
  path_to_file,
  file_exists
)
SELECT unnest(sqlc.arg(first_chars)::text[]),
       unnest(sqlc.arg(performers)::text[]),
       unnest(sqlc.arg(albums)::text[]),
       unnest(sqlc.arg(songs)::text[]),
       unnest(sqlc.arg(paths)::text[]),
       1
ON CONFLICT (path_to_file) DO UPDATE SET file_exists = 1;

-- name: SetMusicID :exec
CALL arabot.set_music_id();