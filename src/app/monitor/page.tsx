import Image from "next/image";
import Link from "next/link";
import React from "react";

export default function MonitorPage() {
  return (
    <div>
      <h1>My Plants</h1>
      <p>This page shows the user's saved plants.</p>
      <nav>
          <ul>
            <li>
                <Link href="/">Home Page</Link>
            </li>
          </ul>
      </nav>
    </div>
  );
}