import { useState, useEffect } from "react";
import ReactPlayer from "react-player";

// ==============================
// > CONSTANTS
// ==============================

const YOUTUBE_VIDEO_REGEX =
  /^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/watch\?v=(.+)$/g;

// ==============================
// > HELPER METHODS
// ==============================

// None yet

// ==============================
// > HOOKS
// ==============================

function useDelayUnmount(isMounted, delayUnmountTime, delayMountTime = 0) {
  const [shouldRender, setShouldRender] = useState(false);

  useEffect(() => {
    let mountTimeoutId;
    let unmountTimeoutId;

    if (isMounted && !shouldRender) {
      mountTimeoutId = setTimeout(() => setShouldRender(true), delayMountTime);
    } else if (!isMounted && shouldRender) {
      unmountTimeoutId = setTimeout(
        () => setShouldRender(false),
        delayUnmountTime
      );
    }

    return () => {
      clearTimeout(unmountTimeoutId);
      clearTimeout(mountTimeoutId);
    };
  }, [isMounted, delayUnmountTime, delayMountTime, shouldRender]);

  return [shouldRender];
}

// ==============================
// > COMPONENTS
// ==============================

function Status({ message, type }) {
  const typeToClass = {
    error: "text-red-800",
    success: "text-green-800",
    info: "text-slate-300",
  };
  return <p className={"text-center p-4 " + typeToClass[type]}>{message}</p>;
}

function YoutubeAcceptor({ onChange, status, hidden }) {
  const [shouldRender] = useDelayUnmount(!hidden, 1200);

  const statusPropsMap = {
    waiting: {
      message: "Paste a YouTube video link above to begin...",
      type: "info",
    },
    error: {
      message: "Please enter a valid YouTube video link.",
      type: "error",
    },
    success: {
      message: "Great! Let's begin.",
      type: "success",
    },
  };

  return (
    shouldRender && (
      <div
        className={`absolute left-0 right-0 transition delay-500 duration-700 ease-in-out ${
          hidden && "opacity-0 translate-y-14"
        }`}
      >
        <input
          className="w-full bg-black border-2 border-gray text-white py-6 mx-6 text-center text-xl placeholder:text-xl placeholder:text-center"
          placeholder="https://youtube.com/watch?v=dQw4w9WgXcQ"
          onChange={onChange}
        />
        <Status {...statusPropsMap[status]} />
      </div>
    )
  );
}

function VideoPlayer({ hidden, link, onFinished }) {
  const [shouldRender] = useDelayUnmount(!hidden, 1200, 1200);
  const [location, setLocation] = useState(0);
  const [confusingLocations, setConfusingLocations] = useState([]);
  const [playing, setPlaying] = useState(true);

  if (!shouldRender) return null;

  const onProgress = (event) => {
    setLocation(event.playedSeconds);
  };

  const markLocation = () => {
    setConfusingLocations([...confusingLocations, location]);
  };

  const handleFinished = () => {
    if (confusingLocations.length == 0) {
      alert("Please mark at least one confusing location.");
      return;
    }
    setPlaying(false);
    onFinished(confusingLocations);
  };

  return (
    <div
      className={
        "w-full transition delay-500 duration-700 ease-in-out px-16" +
        (hidden ? " hidden" : "")
      }
    >
      <ReactPlayer
        url={link}
        width="100%"
        height="60vh"
        playing={playing}
        style={{ minHeight: "300px" }}
        controls
        onProgress={onProgress}
      />
      <div>
        <div className="p-8 pb-4 flex space-x-8">
          <button
            className="flex-1 px-8 py-4 border-2 border-violet-100 text-violet-100 text-2xl transition hover:-translate-y-1"
            onClick={markLocation}
          >
            Mark Confusing Location
          </button>
          <button
            className="flex-1 px-8 py-4 border-2 border-emerald-100 text-emerald-100 text-2xl transition hover:-translate-y-1"
            onClick={handleFinished}
          >
            I'm Finished →
          </button>
        </div>
        <div className="flex space-x-8">
          <p className="flex-1 text-center text-slate-600">
            {confusingLocations.length} Locations Marked
          </p>
          <div className="flex-1"></div>
        </div>
      </div>
    </div>
  );
}

function Result({ result, index }) {
  return (
    <div className="mb-12">
      <h1 className="text-emerald-200 font-bold text-xl mb-1">
        POINT {index + 1}
      </h1>
      <h2 className="text-4xl">{result.query}</h2>
      <h3 className="text-slate-400 text-xl mt-2">
        "{result.transcript_segment}"
      </h3>
      <div className="flex gap-x-8 py-8">
        {result.resources.map((resource) => (
          <a
            className="flex-1 text-left border border-gray-800 transition hover:-translate-y-1"
            href={`https://www.youtube.com/watch?v=${resource.video_id}`}
            target="_blank"
          >
            <img
              style={{ height: 200, objectFit: "cover" }}
              src={resource.thumbnail_url}
            />
            <div className="p-5 border-t border-gray-800">
              <h4 className="text-xl">{resource.title}</h4>
              <p className="text-slate-400 mt-2">{resource.channel_title}</p>
              <p className="text-emerald-50 opacity-50 mt-5">
                {resource.view_count} views
              </p>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

const API_URL = process.env.API_URL || "/";

function VideoResults({ hidden, locations, link }) {
  const [shouldRender] = useDelayUnmount(!hidden, 1200);
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (shouldRender && loading) {
      const videoId = YOUTUBE_VIDEO_REGEX.exec(link)[3];

      fetch(`${API_URL}/recommend`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          videoId,
          comprehensionPoints: locations.map((location) => ({
            comprehension: -1,
            timestamp: location,
          })),
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          setResults(data);
          setLoading(false);
        })
        .catch((error) => {
          window.alert("Something went wrong. Please try again later.");
          console.error("Error:", error);
        });
    }
  }, [shouldRender]);

  if (!shouldRender) return null;

  if (loading) {
    return (
      <div className="w-full transition delay-500 duration-700 ease-in-out px-16">
        <p className="text-center text-slate-300 text-lg animate-pulse">
          Loading (this may take up to 5 minutes)...
        </p>
      </div>
    );
  }

  return (
    <div className="w-full transition delay-500 duration-700 ease-in-out px-16 py-16 pt-44">
      {results.map((result, index) => (
        <Result key={index} result={result} index={index} />
      ))}
    </div>
  );
}

// ==============================
// > APPLICATION
// ==============================

export function App() {
  const [status, setStatus] = useState("waiting"); // waiting, error, success, results
  const [youtubeLink, setYoutubeLink] = useState(null);
  const [locations, setLocations] = useState([]);

  const handleChange = (event) => {
    const youtubeLink = event.target.value;

    // Check if the link is empty and display waiting status again
    if (youtubeLink.length === 0) {
      setStatus("waiting");
      return;
    }

    // Check if the link is a valid YouTube video link
    if (!youtubeLink.match(YOUTUBE_VIDEO_REGEX)) {
      setStatus("error");
      event.target.select();
      return;
    }

    // Otherwise, set the status to success
    setStatus("success");
    setYoutubeLink(youtubeLink);
    event.target.disabled = true;
  };

  const handleFinished = (locations) => {
    setStatus("results");
    setLocations(locations);
  };

  return (
    <div className="flex-1 bg-black text-white min-h-48">
      <div className="max-w-screen-lg mx-auto h-full flex flex-col relative">
        <div className="p-16 absolute w-full">
          <h1 className="text-3xl text-center">PersonaLearn Demo</h1>
        </div>
        <div className="flex-1 flex flex-col justify-center">
          <div className="w-full relative">
            <YoutubeAcceptor
              onChange={handleChange}
              status={status}
              hidden={status === "success" || status === "results"}
            />
            <VideoPlayer
              hidden={status !== "success"}
              link={youtubeLink}
              onFinished={handleFinished}
            />
            <VideoResults
              hidden={status !== "results"}
              locations={locations}
              link={youtubeLink}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
