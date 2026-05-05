//This component establishes a vertical navigation section along the left side of the screen which will be able to be toggled between condensed and expanded sizes
//Last updated 17 September 2025
//Added theme support

import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Cloud,
  FileSearch,
  ShieldCheck,
  Settings,
  User,
  Menu,
  ArrowLeft,
  Search,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

//Button component that we use throughout the sidebar
//Parameters:
//href - link reference
//name - text to display in expanded view
//icon - text to display in collapsed view
type NavButtonProps = {
  href: string;
  name: string;
  icon: LucideIcon;
  isExpanded: boolean;
  isActive?: boolean;
  isDarkMode?: boolean;
  onClick?: (clickEvent: React.MouseEvent<HTMLAnchorElement>) => void;
};

const NavButton: React.FC<NavButtonProps> = ({
  href,
  name,
  icon: Icon,
  isExpanded,
  isActive = false,
  isDarkMode = true,
  onClick,
}) => {
  const handleClick = (clickEvent: React.MouseEvent<HTMLAnchorElement>): void => {
    if (onClick) {
      clickEvent.preventDefault();
      onClick(clickEvent);
    }
  };

  const baseButton = `
    relative flex items-center justify-center
    h-[50px] w-[50px] rounded-[25%]
    text-base font-medium no-underline cursor-pointer
    transition-all duration-300
    hover:-translate-y-0.5
  `;

  const themeButton = isDarkMode
    ? "bg-slate-700 text-white shadow-[0_4px_12px_rgb(0_0_0/0.2)] hover:bg-slate-600 hover:shadow-[0_6px_16px_rgb(0_0_0/0.3)]"
    : "bg-slate-100 text-slate-800 shadow-[0_4px_12px_rgb(0_0_0/0.1)] hover:bg-slate-200 hover:shadow-[0_6px_16px_rgb(0_0_0/0.15)]";

  const expandedButton = isExpanded
    ? "w-[190px] min-w-[190px] max-w-[190px] min-h-[54px] justify-start gap-[15px] rounded-[25px] px-[18px] max-md:min-w-[140px] max-md:px-[15px]"
    : "";

  const activeButton = isActive
    ? "bg-blue-500 shadow-[0_4px_20px_rgb(var(--brand-blue)/0.4)] hover:bg-blue-600"
    : "";

  return (
    <li className="flex justify-center p-0 m-0 w-full">
      <a
        className={`${baseButton} ${themeButton} ${expandedButton} ${activeButton}`}
        href={href}
        onClick={handleClick}
      >
        <span className="flex justify-center items-center w-5 h-5" aria-hidden="true">
          <Icon size={18} strokeWidth={2.2} />
        </span>
        {isExpanded && <span className="text-sm font-medium whitespace-nowrap">{name}</span>}
      </a>
    </li>
  );
};

// Main sidebar component
const SIDEBAR_EXPANDED_KEY = "sidebarExpanded";

type SidebarProps = {
  onWidthChange?: (width: number) => void;
  isDarkMode?: boolean;
};

const Sidebar: React.FC<SidebarProps> = ({ onWidthChange = () => {}, isDarkMode = true }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const [isExpanded, setIsExpanded] = useState<boolean>(() => {
    if (typeof window === "undefined") return true;
    try {
      const stored = window.localStorage.getItem(SIDEBAR_EXPANDED_KEY);
      if (stored === null) return true;
      return stored === "true";
    } catch {
      return true;
    }
  });

  const [searchValue, setSearchValue] = useState<string>("");

  const getActiveItem = (): "home" | "cloud-platforms" | "scans" | "tasks" | "reports" | "settings" | "account" => {
    const path = location.pathname;
    if (path === "/dashboard") return "home";
    if (path === "/cloud-platforms") return "cloud-platforms";
    if (path.startsWith("/scans")) return "scans";
    if (path === "/evidence-scanner") return "tasks";
    if (path === "/reports") return "reports";
    if (path === "/settings") return "settings";
    if (path === "/account") return "account";
    return "home";
  };

  const activeItem = getActiveItem();

  const toggleSidebar = (): void => {
    const newExpanded = !isExpanded;
    setIsExpanded(newExpanded);
    onWidthChange(newExpanded ? 220 : 80);
    if (typeof window !== "undefined") {
      try {
        window.localStorage.setItem(SIDEBAR_EXPANDED_KEY, String(newExpanded));
      } catch {
        // ignore storage errors
      }
    }
  };

  const handleNavClick = (route: string): void => {
    navigate(route);
  };

  const handleSearchChange = (typed: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchValue(typed.target.value);
  };

  const sidebarTheme = isDarkMode
    ? "bg-[rgb(var(--landing-bg-base))] shadow-[4px_0_10px_rgb(0_0_0/0.2)] border-r border-r-slate-400/25"
    : "bg-white shadow-[4px_0_10px_rgb(0_0_0/0.1)] border-r border-r-slate-400/35";

  return (
    <nav
      className={`fixed left-0 top-0 z-1000 h-screen overflow-x-hidden overflow-y-hidden transition-[width,background-color] duration-300 ${
        isExpanded ? "w-55" : "w-20"
      } ${sidebarTheme}`}
    >
      <div className="flex flex-col items-center pt-5 w-full h-screen px-3.75 pb-7.5">
        <div className="flex justify-center mb-10 w-full">
          {isExpanded ? (
            <div
              className={`flex w-full max-w-47.5 items-center rounded-[25px] p-2 transition-all duration-300 hover:-translate-y-0.5 max-md:max-w-37.5 ${
                isDarkMode
                  ? "bg-slate-700 shadow-1 hover:bg-slate-600 hover:shadow-[0_6px_16px_rgb(0_0_0/0.3)]"
                  : "bg-slate-100 shadow-[0_4px_12px_rgb(0_0_0/0.1)] hover:bg-slate-200 hover:shadow-[0_6px_16px_rgb(0_0_0/0.15)]"
              }`}
            >
              <button
                className={`flex h-8.5 w-8.5 shrink-0 items-center justify-center rounded-full transition-colors duration-300 ${
                  isDarkMode
                    ? "bg-slate-600 text-white hover:bg-slate-500"
                    : "bg-slate-200 text-slate-800 hover:bg-slate-300"
                }`}
                onClick={toggleSidebar}
                aria-label="Collapse sidebar"
              >
                <ArrowLeft size={18} />
              </button>

              <input
                type="text"
                placeholder="Search..."
                value={searchValue}
                onChange={handleSearchChange}
                className={`flex-1 bg-transparent px-3 py-2 text-sm outline-none ${
                  isDarkMode ? "text-white placeholder:text-slate-400" : "text-slate-800 placeholder:text-slate-500"
                }`}
              />

              <span className={`${isDarkMode ? "text-slate-400" : "text-slate-500"} pr-2`}>
                <Search size={16} />
              </span>
            </div>
          ) : (
            <button
              className={`flex h-12.5 w-12.5 items-center justify-center rounded-xl transition-all duration-300 hover:-translate-y-0.5 ${
                isDarkMode
                  ? "bg-slate-700 text-white shadow-1 hover:bg-slate-600 hover:shadow-[0_6px_16px_rgb(0_0_0/0.3)]"
                  : "bg-slate-100 text-slate-800 shadow-[0_4px_12px_rgb(0_0_0/0.1)] hover:bg-slate-200 hover:shadow-[0_6px_16px_rgb(0_0_0/0.15)]"
              }`}
              onClick={toggleSidebar}
              aria-label="Expand sidebar"
            >
              <Menu size={18} strokeWidth={2.2} />
            </button>
          )}
        </div>

        <ul className="flex flex-col flex-1 gap-5 items-center p-0 m-0 w-full list-none">
          <NavButton
            href={"/dashboard"}
            name={"Dashboard"}
            icon={LayoutDashboard}
            isExpanded={isExpanded}
            isDarkMode={isDarkMode}
            isActive={activeItem === "home"}
            onClick={() => handleNavClick("/dashboard")}
          />
          <NavButton
            href={"/cloud-platforms"}
            name={"Cloud Platforms"}
            icon={Cloud}
            isExpanded={isExpanded}
            isDarkMode={isDarkMode}
            isActive={activeItem === "cloud-platforms"}
            onClick={() => handleNavClick("/cloud-platforms")}
          />
          <NavButton
            href={"/scans"}
            name={"Scans"}
            icon={FileSearch}
            isExpanded={isExpanded}
            isDarkMode={isDarkMode}
            isActive={activeItem === "scans"}
            onClick={() => handleNavClick("/scans")}
          />
          <NavButton
            href={"/evidence-scanner"}
            name={"Evidence"}
            icon={ShieldCheck}
            isExpanded={isExpanded}
            isDarkMode={isDarkMode}
            isActive={activeItem === "tasks"}
            onClick={() => handleNavClick("/evidence-scanner")}
          />
        </ul>

        <ul
          className={`m-0 mt-auto flex w-full list-none flex-col items-center gap-3.75 p-0 pt-7.5 ${
            isDarkMode ? "border-t border-t-blue-500/15" : "border-t border-t-slate-200"
          }`}
        >
          <NavButton
            href={"/settings"}
            name={"Settings"}
            icon={Settings}
            isExpanded={isExpanded}
            isDarkMode={isDarkMode}
            isActive={activeItem === "settings"}
            onClick={() => handleNavClick("/settings")}
          />
          <NavButton
            href={"/account"}
            name={"Account"}
            icon={User}
            isExpanded={isExpanded}
            isDarkMode={isDarkMode}
            isActive={activeItem === "account"}
            onClick={() => handleNavClick("/account")}
          />
        </ul>
      </div>
    </nav>
  );
};

export default Sidebar;