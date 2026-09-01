import { useRef } from "react";
import { NAV_GROUPS } from "../data.js";
import logo from "../assets/zenve-zippy-logo.png";

export default function Sidebar({ currentKey, onSelect }) {
  const navRef = useRef(null);

  return (
    <aside className="zzc-sidebar">

      {/* Header Area */}
      <div className="zzc-sidebar-header">
        <div className="zzc-logo">
          <img src={logo} alt="Zenve Zippy" />
        </div>

        <div>
          <p className="zzc-brand-title">
            Zenve Zippy CRM
          </p>

          <p className="zzc-brand-sub">
            Cloud control center
          </p>
        </div>
      </div>

      <nav className="zzc-nav" ref={navRef}>
        {NAV_GROUPS.map((group) => (
          <div
            className="zzc-nav-group"
            key={group.label}
          >
            <p className="zzc-nav-group-label">
              {group.label}
            </p>

            {group.items.map((item) => (
              <button
                type="button"
                key={item.key}
                className={
                  "zzc-nav-btn" +
                  (item.key === currentKey ? " active" : "")
                }
                onClick={() => onSelect(item.key)}
              >
                {item.label}
              </button>
            ))}
          </div>
        ))}
      </nav>

    </aside>
  );
}
