import io
import zipfile


def create_zip(files: list[tuple[bytes, str]]) -> bytes:
    buffer = io.BytesIO()
    used_names: set[str] = set()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for content, filename in files:
            name = filename
            counter = 1
            while name in used_names:
                stem, dot, ext = filename.rpartition(".")
                if dot:
                    name = f"{stem}_{counter}.{ext}"
                else:
                    name = f"{filename}_{counter}"
                counter += 1

            used_names.add(name)
            archive.writestr(name, content)

    return buffer.getvalue()
