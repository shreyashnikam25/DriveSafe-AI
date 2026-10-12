"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  Camera,
  Check,
  Eye,
  Settings,
  ShieldCheck,
  Volume2,
  VolumeX,
  X,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";

type MetricProps = {
  label: string;
  value: string;
  unit?: string;
  danger?: boolean;
  icon: React.ReactNode;
};

const PYTHON_STREAM_URL = "http://localhost:8000/video_feed";

export default function Home() {
  const [isDrowsy, setIsDrowsy] = useState(false);
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [useWebcam, setUseWebcam] = useState(true);
  const [muted, setMuted] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const [ear, setEar] = useState("0.34");
  const [blinkRate, setBlinkRate] = useState(14);
  const [headPitch, setHeadPitch] = useState("-1.8");
  const [confidence, setConfidence] = useState("98.8");
  const [fps, setFps] = useState(30);
  const [latency, setLatency] = useState(11);
  const [events, setEvents] = useState(0);
  const [sessionSeconds, setSessionSeconds] = useState(0);

  /* ---------------------------------------------
     SESSION TIMER
  --------------------------------------------- */

  useEffect(() => {
    if (!isMonitoring) return;

    const timer = setInterval(() => {
      setSessionSeconds((value) => value + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [isMonitoring]);

  /* ---------------------------------------------
     DEMO TELEMETRY
     Replace later with your Python API
  --------------------------------------------- */

  useEffect(() => {
    if (!isMonitoring) return;

    const interval = setInterval(() => {
      setFps(Math.floor(28 + Math.random() * 5));
      setLatency(Math.floor(18 + Math.random() * 8));

      if (!isDrowsy) {
        setEar((0.32 + Math.random() * 0.05).toFixed(2));
        setBlinkRate(Math.floor(13 + Math.random() * 4));
        setHeadPitch((-1.5 + Math.random() * 1.5).toFixed(1));
        setConfidence((98 + Math.random() * 1.5).toFixed(1));
      } else {
        setEar((0.10 + Math.random() * 0.05).toFixed(2));
        setBlinkRate(Math.floor(5 + Math.random() * 4));
        setHeadPitch((-16 + Math.random() * 4).toFixed(1));
        setConfidence((93 + Math.random() * 4).toFixed(1));
      }
    }, 500);

    return () => clearInterval(interval);
  }, [isDrowsy, isMonitoring]);

  /* ---------------------------------------------
     DROWSINESS SIMULATION
  --------------------------------------------- */

  const toggleDrowsiness = () => {
    const next = !isDrowsy;

    setIsDrowsy(next);

    if (next) {
      setEvents((value) => value + 1);
      setEar("0.12");
      setBlinkRate(6);
      setHeadPitch("-18.4");
      setConfidence("95.8");
    } else {
      setEar("0.35");
      setBlinkRate(14);
      setHeadPitch("-1.2");
      setConfidence("98.8");
    }
  };

  /* ---------------------------------------------
     TIME
  --------------------------------------------- */

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;

    return `${minutes.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  /* ---------------------------------------------
     METRIC
  --------------------------------------------- */

  const Metric = ({
    label,
    value,
    unit,
    danger,
    icon,
  }: MetricProps) => (
    <motion.div
      layout
      className={`rounded-[22px] p-4 border transition-all duration-300 ${danger
        ? "bg-[#241416] border-[#FF453A]/45"
        : "bg-[#1C1C1E] border-[#38383A]"
        }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-[13px] text-[#98989D]">
          {icon}
          <span>{label}</span>
        </div>

        {danger && (
          <motion.div
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{
              repeat: Infinity,
              duration: 0.8,
            }}
            className="w-2 h-2 rounded-full bg-[#FF453A]"
          />
        )}
      </div>

      <div className="mt-2 flex items-baseline gap-1">
        <span
          className={`text-[26px] font-semibold tracking-tight ${danger ? "text-[#FF453A]" : "text-white"
            }`}
        >
          {value}
        </span>

        {unit && (
          <span className="text-[12px] text-[#636366]">
            {unit}
          </span>
        )}
      </div>
    </motion.div>
  );

  return (
    <main
      className={`h-[100dvh] w-full overflow-hidden bg-black text-white font-sans ${isDrowsy ? "danger-mode" : ""
        }`}
    >
      {/* =========================================
          DANGER EDGE
      ========================================= */}

      <AnimatePresence>
        {isDrowsy && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.2, 0.65, 0.2] }}
            exit={{ opacity: 0 }}
            transition={{
              duration: 0.9,
              repeat: Infinity,
            }}
            className="fixed inset-0 pointer-events-none z-50 border-[5px] border-[#FF453A]"
          />
        )}
      </AnimatePresence>

      {/* =========================================
          TOP BAR
      ========================================= */}

      <header className="h-[62px] px-5 lg:px-7 flex items-center justify-between border-b border-[#2C2C2E] bg-black">
        {/* BRAND */}

        <div className="flex items-center gap-3">
          <motion.div
            animate={
              isDrowsy
                ? {
                  scale: [1, 1.08, 1],
                }
                : {}
            }
            transition={{
              repeat: Infinity,
              duration: 0.8,
            }}
            className={`w-9 h-9 rounded-[12px] flex items-center justify-center ${isDrowsy
              ? "bg-[#FF453A]"
              : "bg-[#1C1C1E]"
              }`}
          >
            <ShieldCheck className="w-[19px] h-[19px]" />
          </motion.div>

          <div>
            <div className="text-[15px] font-semibold tracking-tight">
              DriveSafe
            </div>

            <div className="text-[11px] text-[#636366]">
              Driver monitoring
            </div>
          </div>
        </div>

        {/* CENTER STATUS */}

        <div
          className={`hidden sm:flex items-center gap-2 px-4 py-2 rounded-full border ${isDrowsy
            ? "bg-[#241416] border-[#FF453A]/50 text-[#FF453A]"
            : "bg-[#1C1C1E] border-[#38383A] text-[#30D158]"
            }`}
        >
          <motion.span
            animate={
              isDrowsy
                ? {
                  scale: [1, 1.5, 1],
                }
                : {
                  opacity: [0.4, 1, 0.4],
                }
            }
            transition={{
              repeat: Infinity,
              duration: isDrowsy ? 0.6 : 1.5,
            }}
            className={`w-2 h-2 rounded-full ${isDrowsy
              ? "bg-[#FF453A]"
              : "bg-[#30D158]"
              }`}
          />

          <span className="text-[12px] font-medium">
            {isDrowsy
              ? "Drowsiness detected"
              : "Monitoring active"}
          </span>
        </div>

        {/* ACTIONS */}

        <div className="flex items-center gap-2">
          <button
            onClick={() => setUseWebcam(!useWebcam)}
            className="h-9 px-3 rounded-full bg-[#1C1C1E] border border-[#38383A] hover:bg-[#2C2C2E] transition flex items-center gap-2 text-[12px]"
          >
            <Camera className="w-4 h-4" />

            <span className="hidden md:inline">
              {useWebcam ? "Live Camera" : "Demo"}
            </span>
          </button>

          <button
            onClick={() => setMuted(!muted)}
            className="w-9 h-9 rounded-full bg-[#1C1C1E] border border-[#38383A] flex items-center justify-center hover:bg-[#2C2C2E]"
          >
            {muted ? (
              <VolumeX className="w-4 h-4 text-[#FF453A]" />
            ) : (
              <Volume2 className="w-4 h-4 text-[#30D158]" />
            )}
          </button>

          <button
            onClick={() => setShowSettings(true)}
            className="w-9 h-9 rounded-full bg-[#1C1C1E] border border-[#38383A] flex items-center justify-center hover:bg-[#2C2C2E]"
          >
            <Settings className="w-4 h-4 text-[#AEAEB2]" />
          </button>
        </div>
      </header>

      {/* =========================================
          MAIN
      ========================================= */}

      <section className="h-[calc(100dvh-104px)] p-4 lg:p-5">
        <div className="h-full grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_330px] gap-4">

          {/* =====================================
              CAMERA
          ===================================== */}

          <div
            className={`relative min-h-0 rounded-[30px] overflow-hidden border ${isDrowsy
              ? "border-[#FF453A]/70 bg-[#11090A]"
              : "border-[#2C2C2E] bg-[#080808]"
              }`}
          >
            {useWebcam ? (
              /* =================================
                 PYTHON OPENCV STREAM
              ================================= */

              <div className="absolute inset-0 bg-black">
                <img
                  src={PYTHON_STREAM_URL}
                  alt="DriveSafe AI driver camera"
                  className="absolute inset-0 h-full w-full object-cover object-center"
                />
              </div>
            ) : (
              /* =================================
                 DEMO CAMERA
              ================================= */

              <div className="absolute inset-0 bg-[#090909]">
                <div className="absolute inset-0 flex items-center justify-center">
                  <motion.div
                    animate={{
                      y: isDrowsy ? 8 : 0,
                      scale: isDrowsy ? 0.98 : 1,
                    }}
                    transition={{
                      duration: 0.5,
                    }}
                    className="relative w-[190px] h-[250px]"
                  >
                    {/* FACE */}

                    <div
                      className={`absolute inset-0 rounded-[48%] border-[2px] ${isDrowsy
                        ? "border-[#FF453A]"
                        : "border-[#30D158]"
                        }`}
                    />

                    {/* LEFT EYE */}

                    <motion.div
                      animate={{
                        scaleY: isDrowsy ? 0.12 : 1,
                      }}
                      className={`absolute top-[92px] left-[43px] w-[30px] h-[14px] rounded-full border ${isDrowsy
                        ? "border-[#FF453A]"
                        : "border-[#30D158]"
                        }`}
                    />

                    {/* RIGHT EYE */}

                    <motion.div
                      animate={{
                        scaleY: isDrowsy ? 0.12 : 1,
                      }}
                      className={`absolute top-[92px] right-[43px] w-[30px] h-[14px] rounded-full border ${isDrowsy
                        ? "border-[#FF453A]"
                        : "border-[#30D158]"
                        }`}
                    />

                    {/* NOSE */}

                    <div
                      className={`absolute top-[122px] left-1/2 -translate-x-1/2 w-[2px] h-[30px] ${isDrowsy
                        ? "bg-[#FF453A]"
                        : "bg-[#30D158]"
                        }`}
                    />

                    {/* MOUTH */}

                    <div
                      className={`absolute bottom-[57px] left-1/2 -translate-x-1/2 w-[42px] h-[12px] rounded-full border ${isDrowsy
                        ? "border-[#FF453A]"
                        : "border-[#30D158]"
                        }`}
                    />
                  </motion.div>
                </div>

                <TrackingCorners danger={isDrowsy} />

                <div className="absolute bottom-5 left-5 flex items-center gap-2 text-[11px] text-[#98989D]">
                  <div
                    className={`w-2 h-2 rounded-full ${isDrowsy
                      ? "bg-[#FF453A]"
                      : "bg-[#30D158]"
                      }`}
                  />

                  DEMO CAMERA
                </div>
              </div>
            )}

            {/* CAMERA HEADER */}

            <div className="absolute top-4 left-4 right-4 flex justify-between items-center pointer-events-none">
              <div className="px-3 py-2 rounded-full bg-black/70 border border-white/10 text-[11px] text-[#AEAEB2]">
                LIVE CAMERA
              </div>

              <div className="px-3 py-2 rounded-full bg-black/70 border border-white/10 text-[11px] text-[#AEAEB2]">
                {fps} FPS · {latency} ms
              </div>
            </div>

            {/* =================================
                DANGER BANNER
            ================================= */}

            <AnimatePresence>
              {isDrowsy && (
                <motion.div
                  initial={{
                    y: 40,
                    opacity: 0,
                    scale: 0.96,
                  }}
                  animate={{
                    y: 0,
                    opacity: 1,
                    scale: 1,
                  }}
                  exit={{
                    y: 40,
                    opacity: 0,
                    scale: 0.96,
                  }}
                  className="absolute bottom-5 left-1/2 -translate-x-1/2 w-[min(520px,calc(100%-32px))]"
                >
                  <motion.div
                    animate={{
                      boxShadow: [
                        "0 10px 30px rgba(255,69,58,0.2)",
                        "0 10px 60px rgba(255,69,58,0.55)",
                        "0 10px 30px rgba(255,69,58,0.2)",
                      ],
                    }}
                    transition={{
                      repeat: Infinity,
                      duration: 1,
                    }}
                    className="bg-[#FF453A] text-white rounded-[22px] px-5 py-4 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <motion.div
                        animate={{
                          rotate: [-5, 5, -5],
                        }}
                        transition={{
                          repeat: Infinity,
                          duration: 0.3,
                        }}
                      >
                        <AlertTriangle className="w-6 h-6" />
                      </motion.div>

                      <div>
                        <div className="font-bold text-[14px]">
                          Drowsiness detected
                        </div>

                        <div className="text-[11px] text-white/80">
                          Please take a break.
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={toggleDrowsiness}
                      className="bg-white text-[#FF453A] rounded-full px-4 py-2 text-[11px] font-semibold hover:bg-[#F2F2F7]"
                    >
                      Dismiss
                    </button>
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* =====================================
              RIGHT PANEL
          ===================================== */}

          <aside className="min-h-0 flex flex-col gap-3">

            {/* STATUS */}

            <motion.div
              layout
              className={`rounded-[28px] border p-5 ${isDrowsy
                ? "bg-[#241416] border-[#FF453A]/50"
                : "bg-[#1C1C1E] border-[#38383A]"
                }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[12px] text-[#98989D]">
                  SAFETY STATUS
                </span>

                {isDrowsy ? (
                  <AlertTriangle className="w-5 h-5 text-[#FF453A]" />
                ) : (
                  <Check className="w-5 h-5 text-[#30D158]" />
                )}
              </div>

              <AnimatePresence mode="wait">
                {isDrowsy ? (
                  <motion.div
                    key="danger"
                    initial={{
                      opacity: 0,
                      y: 5,
                    }}
                    animate={{
                      opacity: 1,
                      y: 0,
                    }}
                    exit={{
                      opacity: 0,
                    }}
                    className="mt-4"
                  >
                    <h1 className="text-[28px] leading-none font-semibold tracking-tight text-[#FF453A]">
                      Drowsy
                    </h1>

                    <p className="mt-2 text-[12px] text-[#AEAEB2]">
                      Eye closure and head position indicate possible
                      drowsiness.
                    </p>
                  </motion.div>
                ) : (
                  <motion.div
                    key="safe"
                    initial={{
                      opacity: 0,
                      y: 5,
                    }}
                    animate={{
                      opacity: 1,
                      y: 0,
                    }}
                    exit={{
                      opacity: 0,
                    }}
                    className="mt-4"
                  >
                    <h1 className="text-[28px] leading-none font-semibold tracking-tight">
                      Attentive
                    </h1>

                    <p className="mt-2 text-[12px] text-[#98989D]">
                      Driver appears alert and focused.
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* METRICS */}

            <div className="grid grid-cols-2 gap-3">
              <Metric
                label="EAR"
                value={ear}
                unit="/ 0.40"
                danger={isDrowsy}
                icon={
                  <Eye className="w-3.5 h-3.5" />
                }
              />

              <Metric
                label="Confidence"
                value={confidence}
                unit="%"
                icon={
                  <ShieldCheck className="w-3.5 h-3.5" />
                }
              />

              <Metric
                label="Blink rate"
                value={blinkRate.toString()}
                unit="bpm"
                icon={
                  <Activity className="w-3.5 h-3.5" />
                }
              />

              <Metric
                label="Head pitch"
                value={headPitch}
                unit="°"
                danger={isDrowsy}
                icon={
                  <Zap className="w-3.5 h-3.5" />
                }
              />
            </div>

            {/* SESSION */}

            <div className="flex-1 min-h-0 rounded-[28px] bg-[#1C1C1E] border border-[#38383A] p-5 flex flex-col justify-between">
              <div>
                <div className="text-[12px] text-[#98989D]">
                  MONITORING SESSION
                </div>

                <div className="mt-3 text-[32px] font-semibold tracking-tight">
                  {formatTime(sessionSeconds)}
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between text-[12px]">
                  <span className="text-[#98989D]">
                    Drowsy events
                  </span>

                  <span className="font-medium">
                    {events}
                  </span>
                </div>

                <div className="flex items-center justify-between text-[12px]">
                  <span className="text-[#98989D]">
                    Detection engine
                  </span>

                  <span className="text-[#30D158]">
                    CNN Active
                  </span>
                </div>

                <div className="flex items-center justify-between text-[12px]">
                  <span className="text-[#98989D]">
                    Camera source
                  </span>

                  <span className="text-[#30D158]">
                    OpenCV
                  </span>
                </div>

                <button
                  onClick={toggleDrowsiness}
                  className={`w-full h-11 rounded-full font-semibold text-[12px] transition ${isDrowsy
                    ? "bg-[#30D158] text-black hover:bg-[#63E37C]"
                    : "bg-[#FF453A] text-white hover:bg-[#FF5B52]"
                    }`}
                >
                  {isDrowsy
                    ? "Simulate Attentive State"
                    : "Simulate Drowsiness"}
                </button>
              </div>
            </div>
          </aside>
        </div>
      </section>

      {/* =========================================
          FOOTER
      ========================================= */}

      <footer className="h-[42px] px-5 lg:px-7 border-t border-[#2C2C2E] flex items-center justify-between text-[11px] text-[#636366]">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span
              className={`w-1.5 h-1.5 rounded-full ${isDrowsy
                ? "bg-[#FF453A]"
                : "bg-[#30D158]"
                }`}
            />

            Python AI Camera
          </span>

          <span className="hidden sm:block">
            Face &amp; eye tracking
          </span>
        </div>

        <div>
          {fps} FPS · {latency} ms
        </div>
      </footer>

      {/* =========================================
          SETTINGS
      ========================================= */}

      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] bg-black/75 flex items-center justify-center p-5"
          >
            <motion.div
              initial={{
                scale: 0.94,
                y: 12,
              }}
              animate={{
                scale: 1,
                y: 0,
              }}
              exit={{
                scale: 0.94,
                y: 12,
              }}
              className="w-full max-w-[390px] rounded-[30px] bg-[#1C1C1E] border border-[#38383A] p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-semibold">
                    Settings
                  </h2>

                  <p className="text-[12px] text-[#98989D] mt-1">
                    Driver monitoring
                  </p>
                </div>

                <button
                  onClick={() => setShowSettings(false)}
                  className="w-9 h-9 rounded-full bg-[#2C2C2E] flex items-center justify-center"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-6 space-y-2">
                <SettingRow
                  icon={<Eye />}
                  title="EAR threshold"
                  value="< 0.85"
                />

                <SettingRow
                  icon={<Activity />}
                  title="Detection mode"
                  value="Continuous"
                />

                <SettingRow
                  icon={
                    muted ? (
                      <VolumeX />
                    ) : (
                      <Volume2 />
                    )
                  }
                  title="Alarm"
                  value={
                    muted
                      ? "Muted"
                      : "Enabled"
                  }
                />

                <SettingRow
                  icon={<Camera />}
                  title="Camera source"
                  value="OpenCV"
                />
              </div>

              <button
                onClick={() =>
                  setShowSettings(false)
                }
                className="mt-6 w-full h-11 rounded-full bg-white text-black text-[12px] font-semibold"
              >
                Done
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}

/* =============================================
   TRACKING CORNERS
============================================= */

function TrackingCorners({
  danger,
}: {
  danger: boolean;
}) {
  const color = danger
    ? "border-[#FF453A]"
    : "border-[#30D158]";

  return (
    <div className="absolute inset-[18%] pointer-events-none">
      <div
        className={`absolute top-0 left-0 w-7 h-7 border-l-2 border-t-2 ${color}`}
      />

      <div
        className={`absolute top-0 right-0 w-7 h-7 border-r-2 border-t-2 ${color}`}
      />

      <div
        className={`absolute bottom-0 left-0 w-7 h-7 border-l-2 border-b-2 ${color}`}
      />

      <div
        className={`absolute bottom-0 right-0 w-7 h-7 border-r-2 border-b-2 ${color}`}
      />
    </div>
  );
}

/* =============================================
   SETTINGS ROW
============================================= */

function SettingRow({
  icon,
  title,
  value,
}: {
  icon: React.ReactNode;
  title: string;
  value: string;
}) {
  return (
    <div className="h-14 rounded-[17px] bg-[#2C2C2E] px-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="text-[#98989D] [&_svg]:w-4 [&_svg]:h-4">
          {icon}
        </div>

        <span className="text-[13px]">
          {title}
        </span>
      </div>

      <span className="text-[12px] text-[#98989D]">
        {value}
      </span>
    </div>
  );
}