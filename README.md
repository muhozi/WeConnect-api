# WeConnect 
[![Build Status](https://travis-ci.org/muhozi/WeConnect-2.svg?branch=master)](https://travis-ci.org/muhozi/WeConnect-2)
[![Coverage Status](https://coveralls.io/repos/github/muhozi/WeConnect-2/badge.svg)](https://coveralls.io/github/muhozi/WeConnect-2)
[![codecov](https://codecov.io/gh/muhozi/WeConnect-2/branch/master/graph/badge.svg)](https://codecov.io/gh/muhozi/WeConnect-2)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/430f61e8095c42978b9461b03b7570ae)](https://www.codacy.com/app/muhozi/WeConnect-2?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=muhozi/WeConnect-2&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/4fed0cd96ad48633a616/maintainability)](https://codeclimate.com/github/muhozi/WeConnect-2/maintainability)


WeConnect provides a platform that brings businesses and individuals together. This platform creates awareness for businesses and gives the users the ability to write reviews about the businesses they have interacted with. 

## API

![Docs](docs.png "Docs")



**TL**;**DR** Check the API docs at https://allconnect.herokuapp.com/api/v1 

### Set up the environment

This platform API is built on the top Flask python web framework.

Clone the repository

```sh
git clone git@github.com:muhozi/WeConnect-2.git
```

Create the virtual environment and install dependencies(These are required Python,pip and virtual environment):

```sh
cd WeConnect
```

```sh
virtualenv env
```

Activate the virtual environment [For windows]

```sh
cd env/Scripts && activate && cd ../..
```

Install dependencies using pip

```sh
pip install -r requirements.txt
```

Add required environment variables:

You may use `.env` configuration file (Loaded using [python-dotenv](https://github.com/theskumar/python-dotenv)):

Create file name it `.env` and add the following contents:

```con
DEBUG=True
SECRET_KEY=any_chosen_secret_key
```

**OR**

***On windows(cmd)*:**

```powershell
SET SECRET_KEY=any_chosen_secret_key
```

```powershell
SET DEBUG=True
```

***On Unix based system*:**

```sh
export SECRET_KEY=any_chosen_secret_key
```

```sh
export DEBUG=True
```



### Run the application

To run the tests, use `nosetests` or any other test runner of your choice

```sh
nosetests -v
```

Then run the app

```sh
python app.py
```



### View API usage (Documentation)

View the API usage (Documentation) in a browser via: http://127.0.0.1:5000/api/v1



### API Endpoints

**`POST /api/v1/auth/register`** *User registration*

**`POST /api/v1/auth/login`** *User login*

**`GET /api/v1/businesses/<business-id>/reviews`** *Get all the reviews about a business*

**`GET /api/v1/businesses/<business-id>`** *Get a business details*

<u>**Protected endpoints**</u>: Access token is required (`Authorization` header token)

**`POST /api/v1/auth/logout`** *User logout*

**`POST /api/v1/auth/reset-password`** *Change password*

**`POST /api/v1/businesses`** *Register business*

**`PUT /api/v1/businesses/<business-id>`** *Update business details*

**`DELETE /api/v1/businesses/<business-id>`** *Delete business*

**`GET /api/v1/businesses`** *Get your registered businesses*

**`POST /api/v1/businesses/<business-id>/reviews`** *Post a review about business*





> The above endpoints may be accessed on Heroku, the base URL is https://allconnect.herokuapp.com
>
> Also you may read and try out the detailed usage of the API through its documentation at 
>
>  https://allconnect.herokuapp.com/api/v1





## User Interface

WeConnect use the following UI technology:

- CSS, HTML, JS


- [Bootstrap 4](https://getbootstrap.com/) (HTML, CSS, and JS Framework to develop UI) 
- Font icons : [Ionicons](http://ionicons.com/)

Have a look at  the UI follow the link for a demo **[Demo](https:///muhozi.github.io/WeConnect/templates)**



## Author

Emery Muhozi



## License

MIT License