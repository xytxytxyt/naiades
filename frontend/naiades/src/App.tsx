import { useEffect, useState } from 'react';
import './App.css';

export const backendHost = `http://${import.meta.env.VITE_BACKEND_HOST}:8001`;

interface DownloadSubdir {
  data: {
    name: string,
    most_recent_file: string,
    date_time: string,
  }
}

export default function App() {
  const [downloads, setDownloads] = useState<Record<string, DownloadSubdir[]>>({});
  useEffect(
    () => {
      console.log("fetching the latest");
      fetch(
        `${backendHost}/downloads`,
        {
          headers: {
            'Accept': 'application/json',
          },
        }
      ).then(response => {
        return response.json() as Promise<Record<string, DownloadSubdir[]>>;
      }).then(downloadsResponse => {
        setDownloads(downloadsResponse);
      });
    },
    [],
  );

  return (
    <>
      <div>
        <h1>The Latest</h1>
        {(Object.keys(downloads).length > 0) && Object.keys(downloads).map((downloadDir) => {
          let downloadSubdirs = downloads[downloadDir];
          return (
            <div key={downloadDir}>
              <h2>{downloadDir}</h2>
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Most Recent File</th>
                    <th>Modified Time</th>
                  </tr>
                </thead>
                <tbody>
                  {downloadSubdirs && downloadSubdirs.map((downloadSubdir) => {
                    return (
                      <tr key={downloadSubdir.data.name}>
                        <td>{downloadSubdir.data.name}</td>
                        <td>{downloadSubdir.data.most_recent_file}</td>
                        <td>{downloadSubdir.data.date_time}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          );
        })}
      </div>
    </>
  )
}
