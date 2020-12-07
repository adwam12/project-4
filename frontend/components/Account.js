import React, { useState, useEffect } from 'react'
import axios from 'axios'


const Account = () => {
  const [userData, setUserData] = useState([])

  const userId = localStorage.getItem('user_id')

  useEffect(() => {
    axios.get(`api/users/${userId}`)
      .then(resp => {
        console.log(resp.data)
        setUserData(resp.data)
      })
  }, [])



  if (userData === []) {
    return <div className="section">
      <div className="container">
        <div className="title">
          Loading ...
        </div>
        <progress className="progress is-small is-link" max="100">60%</progress>
      </div>
    </div>
  }

  return <section className='section mt-6'>
    <h1 className="title">Contacts</h1>


    <button onClick={() => {
      
      userData.contacts.map((contact, index) => {
        return <div key={index} >{contact.name}
          </div>
    }
    )
      
      console.log(userData.contacts)
    }
      }>Test</button>


    
        <article className="media">
          {/* <figure className="media-left">
            <p className="image is-64x64">
              <img src="https://bulma.io/images/placeholders/128x128.png"/>
            </p>
          </figure> */}
          <div className="media-content">
            <div className="content">
              <p>
                <strong>John Smith</strong> <small>@johnsmith</small> <small>31m</small>
                <br/>
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin ornare magna eros, eu pellentesque tortor vestibulum ut. Maecenas non massa sem. Etiam finibus odio quis feugiat facilisis.
              </p>
            </div>
            <nav className="level is-mobile">
              <div className="level-left">
                <a className="level-item">
                  <span className="icon is-small"><i className="fas fa-reply"></i></span>
                </a>
                <a className="level-item">
                  <span className="icon is-small"><i className="fas fa-retweet"></i></span>
                </a>
                <a className="level-item">
                  <span className="icon is-small"><i className="fas fa-heart"></i></span>
                </a>
              </div>
            </nav>
          </div>
          <div className="media-right">
            <button className="delete"></button>
          </div>
        </article>
 
  
  
  </section>
  
  
  {/* <div className="section">
    <div className="container">
      
      <div className="notifications is-primary">
        {userData.contacts.map((contact, index) => {
          return <div key={index} >
            <Link to={`/locations/${location._id}`}>
            <div className="tile is-parent px-0">
              <div className="tile is-child box">

                <div className="columns">
                  <div className="column">
                    <p className="title is-4">{location.name}</p>
                    <div className="tags">
                      {location.category.map((category, index) => {
                        return <div className="tag is-warning" key={index}>
                          {category}
                        </div>
                      })}
                    </div>
                    <p className="subtitle is-6">{'City: ' + location.city}</p>
                    {location.bio && <p className="subtitle is-6">{'About: ' + location.bio}</p>}
                  </div>
                  <div className="column">
                    {location.image && <img className="locationsImage" src={location.image} alt={location.name} />}
                  </div>

                </div>
              </div>
        
            </div>
            </Link>
          </div>
        })}
      </div>
  
    </div>
  </div> */}



}

export default Account