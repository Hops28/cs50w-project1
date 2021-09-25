# Project 1

Programación web con python

- Login, Logout y Register
- Deberás crear una cuenta o usar una cuenta ya existente para poder iniciar sesión
- Una vez iniciada la sesión, podrás ver todos los libros que están importados en la base de datos
- Si colocas algún texto dentro del buscador, comenzará a mostrar todas las coincidencias según el título, el autor o el isbn
- Si das click a uno de los libros en la lista, se mostrará una página donde se mostrarán los detalles del libro:
  - Title
  - ISBN
  - Author
  - Year
  - Thumbnail
  - Description
- También están la parte donde se podrán ver las diferentes reseñas que se han publicado al libro seleccionado
- Si ya se puso una reseña, entonces no se podrá agregar otra, cada usuario solamente podrá colocar una sola reseña para cada libro

- Todos estos datos como los de los libros, los usuarios y las reseñas, están guardadas en una base de datos
- Donde hay tres tablas: "Book", "User" y "Comment"
- En el cual, sólo se le aplicó la normalización a la tabla "Comment" con dos claves primarias "IdUser" y "IdBook"
- Donde para revisar si el usuario ya comentó o no, se hizo la validación en python
- Con la API se obtuvieron más detalles de cada libro por mostrar, como la descripción, las valoraciones, su promedio y una imagen que representa el libro
