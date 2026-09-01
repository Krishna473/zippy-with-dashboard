import React from "react";

function Navbar({ activeItem }) {
  return (
    <header className="navbar">

      <div className="navbar-title">
        <h1>{activeItem}</h1>
      </div>

      <div className="navbar-actions">

        <input
          type="text"
          placeholder="Search full_name"
          className="search-input"
        />

        <button className="primary-button">
          New record
        </button>

        <button className="nav-button active">
          Dashboard
        </button>

        <button className="nav-button active">
          Data
        </button>

        <button className="nav-button active">
          Bulk tools
        </button>

        <button className="nav-button">
          Sales CRM
        </button>

        <button className="nav-button">
          Console
        </button>

      </div>

    </header>
  );
}

export default Navbar;